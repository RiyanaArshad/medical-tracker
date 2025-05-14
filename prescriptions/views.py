from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Prescription, MedicationReminder
from .forms import PrescriptionForm, MedicationReminderForm
from accounts.models import PATIENT, DOCTOR, ADMIN

@login_required
def prescription_list(request):
    user_profile = request.user.profile
    
    if user_profile.is_patient():
        # Patients can only see their own prescriptions
        prescriptions = Prescription.objects.filter(patient=request.user)
    elif user_profile.is_doctor():
        # Doctors can see prescriptions they wrote
        prescriptions = Prescription.objects.filter(doctor=request.user)
    elif user_profile.is_admin():
        # Admins can see all prescriptions
        prescriptions = Prescription.objects.all()
    else:
        return HttpResponseForbidden()
    
    context = {
        'prescriptions': prescriptions,
        'active_prescriptions': prescriptions.filter(is_active=True),
        'is_patient': user_profile.is_patient(),
    }
    
    return render(request, 'prescriptions/prescription_list.html', context)

@login_required
def prescription_create(request):
    user_profile = request.user.profile
    
    # Only doctors can create prescriptions
    if not user_profile.is_doctor():
        messages.error(request, 'Only doctors can create prescriptions.')
        return redirect('prescription_list')
    
    # Get medical record if provided
    medical_record = None
    patient = None
    if 'medical_record_id' in request.GET:
        from medical_records.models import MedicalRecord
        medical_record = get_object_or_404(MedicalRecord, id=request.GET['medical_record_id'])
        patient = medical_record.patient
    elif 'patient_id' in request.GET:
        from django.contrib.auth.models import User
        patient = get_object_or_404(User, id=request.GET['patient_id'])
    
    if request.method == 'POST':
        # Debug info
        messages.info(request, f'POST data: {dict(request.POST.items())}')
        messages.info(request, f'Medical record ID: {request.GET.get("medical_record_id")}')
        messages.info(request, f'Patient ID: {request.GET.get("patient_id")}')
        
        # Create form with initial data
        initial_data = {
            'patient': patient.id if patient else None,
            'medical_record': medical_record.id if medical_record else None,
            'doctor': request.user.id,  # Set the current doctor
        }
        
        # Merge POST data with initial data
        post_data = request.POST.copy()
        for key, value in initial_data.items():
            if value is not None and key not in post_data:
                post_data[key] = value
        
        form = PrescriptionForm(post_data, doctor=request.user)
        if form.is_valid():
            try:
                prescription = form.save()
                messages.success(request, 'Prescription created successfully!')
                return redirect('prescription_detail', prescription_id=prescription.id)
            except Exception as e:
                messages.error(request, f'Error saving prescription: {str(e)}')
                # Print stack trace for debugging
                import traceback
                messages.error(request, f'Stack trace: {traceback.format_exc()}')
        else:
            # Add form errors to messages for debugging
            messages.error(request, f'Form is not valid. Cleaned data: {form.cleaned_data if hasattr(form, "cleaned_data") else "No cleaned data"}')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        # Pre-populate patient field if it's in the query params
        initial = {}
        if 'patient_id' in request.GET:
            initial['patient'] = request.GET['patient_id']
        if medical_record:
            initial['medical_record'] = medical_record.id
            initial['patient'] = medical_record.patient.id  # Also set the patient from medical record
            
        form = PrescriptionForm(initial=initial, doctor=request.user)
    
    context = {
        'form': form,
        'record': medical_record
    }
    return render(request, 'prescriptions/prescription_form.html', context)

@login_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    user_profile = request.user.profile
    
    # Check permissions
    if user_profile.is_patient() and prescription.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and prescription.doctor != request.user:
        return HttpResponseForbidden()
    
    reminders = prescription.reminders.all()
    
    return render(request, 'prescriptions/prescription_detail.html', {
        'prescription': prescription,
        'reminders': reminders
    })

@login_required
def prescription_update(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    user_profile = request.user.profile
    
    # Check permissions (only doctors who created the prescription and admins can update)
    if user_profile.is_doctor() and prescription.doctor != request.user:
        return HttpResponseForbidden()
    elif not (user_profile.is_doctor() or user_profile.is_admin()):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription, doctor=request.user if user_profile.is_doctor() else None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prescription updated successfully!')
            return redirect('prescription_detail', prescription_id=prescription.id)
    else:
        form = PrescriptionForm(instance=prescription, doctor=request.user if user_profile.is_doctor() else None)
    
    return render(request, 'prescriptions/prescription_form.html', {
        'form': form,
        'prescription': prescription
    })

@login_required
def reminder_create(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    user_profile = request.user.profile
    
    # Check permissions (patients can create reminders for their prescriptions)
    if user_profile.is_patient() and prescription.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and prescription.doctor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = MedicationReminderForm(request.POST, prescription=prescription)
        if form.is_valid():
            reminder = form.save()
            messages.success(request, 'Reminder added successfully!')
            return redirect('prescription_detail', prescription_id=prescription.id)
    else:
        form = MedicationReminderForm(prescription=prescription)
    
    return render(request, 'prescriptions/reminder_form.html', {
        'form': form,
        'prescription': prescription
    })

@login_required
def reminder_update(request, reminder_id):
    reminder = get_object_or_404(MedicationReminder, id=reminder_id)
    prescription = reminder.prescription
    user_profile = request.user.profile
    
    # Check permissions
    if user_profile.is_patient() and prescription.patient != request.user:
        return HttpResponseForbidden()
    elif user_profile.is_doctor() and prescription.doctor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = MedicationReminderForm(request.POST, instance=reminder, prescription=prescription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder updated successfully!')
            return redirect('prescription_detail', prescription_id=prescription.id)
    else:
        form = MedicationReminderForm(instance=reminder, prescription=prescription)
    
    return render(request, 'prescriptions/reminder_form.html', {
        'form': form,
        'prescription': prescription,
        'reminder': reminder
    })
