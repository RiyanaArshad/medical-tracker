from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, FileResponse

from .models import MedicalRecord, MedicalReport
from .forms import MedicalRecordForm, MedicalReportForm
from accounts.models import PATIENT, DOCTOR, ADMIN

@login_required
def medical_record_list(request):
    user_profile = request.user.profile
    
    if user_profile.is_patient():
        # Patients can only see their own records
        records = MedicalRecord.objects.filter(patient=request.user)
    elif user_profile.is_doctor():
        # Doctors can see records they created
        records = MedicalRecord.objects.filter(doctor=request.user)
    elif user_profile.is_admin():
        # Admins can see all records
        records = MedicalRecord.objects.all()
    else:
        return HttpResponseForbidden()
    
    return render(request, 'medical_records/record_list.html', {'records': records})

@login_required
def medical_record_detail(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    user_profile = request.user.profile
    
    # Check permissions
    if user_profile.is_patient() and record.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and record.doctor != request.user:
        return HttpResponseForbidden()
    
    reports = record.reports.all()
    
    return render(request, 'medical_records/record_detail.html', {
        'record': record,
        'reports': reports
    })

@login_required
def medical_record_create(request):
    user_profile = request.user.profile
    
    # Only doctors and admins can create medical records
    if not (user_profile.is_doctor() or user_profile.is_admin()):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        if user_profile.is_doctor():
            form = MedicalRecordForm(request.POST, doctor=request.user)
        else:
            form = MedicalRecordForm(request.POST)
        
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Medical record created successfully!')
            return redirect('medical_record_detail', record_id=record.id)
    else:
        if user_profile.is_doctor():
            form = MedicalRecordForm(doctor=request.user)
        else:
            form = MedicalRecordForm()
    
    return render(request, 'medical_records/record_form.html', {'form': form})

@login_required
def medical_record_update(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    user_profile = request.user.profile
    
    # Check permissions
    if user_profile.is_doctor() and record.doctor != request.user:
        return HttpResponseForbidden()
    elif not (user_profile.is_doctor() or user_profile.is_admin()):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medical record updated successfully!')
            return redirect('medical_record_detail', record_id=record.id)
    else:
        form = MedicalRecordForm(instance=record)
    
    return render(request, 'medical_records/record_form.html', {
        'form': form,
        'record': record
    })

@login_required
def medical_report_create(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    user_profile = request.user.profile
    
    # Check permissions
    if user_profile.is_patient() and record.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and record.doctor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES, medical_record=record, user=request.user)
        if form.is_valid():
            report = form.save()
            messages.success(request, 'Medical report uploaded successfully!')
            return redirect('medical_record_detail', record_id=record.id)
    else:
        form = MedicalReportForm(medical_record=record, user=request.user)
    
    return render(request, 'medical_records/report_form.html', {
        'form': form,
        'record': record
    })

@login_required
def medical_report_detail(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id)
    user_profile = request.user.profile
    # Check permissions
    if user_profile.is_patient() and report.medical_record.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and report.medical_record.doctor != request.user:
        return HttpResponseForbidden()
    return render(request, 'medical_records/report_detail.html', {'report': report})

@login_required
def report_download(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id)
    user_profile = request.user.profile
    # Check permissions
    if user_profile.is_patient() and report.medical_record.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and report.medical_record.doctor != request.user:
        return HttpResponseForbidden()
    if not report.report_file:
        return HttpResponseForbidden()
    response = FileResponse(report.report_file.open('rb'), as_attachment=True, filename=report.report_file.name.split('/')[-1])
    return response

@login_required
def report_view(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id)
    user_profile = request.user.profile
    # Check permissions
    if user_profile.is_patient() and report.medical_record.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and report.medical_record.doctor != request.user:
        return HttpResponseForbidden()
    if not report.report_file:
        return HttpResponseForbidden()
    response = FileResponse(report.report_file.open('rb'), as_attachment=False, filename=report.report_file.name.split('/')[-1])
    return response
