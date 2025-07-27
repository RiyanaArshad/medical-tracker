from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import date

from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, 
    PatientProfileForm, DoctorProfileForm, 
    UserProfileForm, UserBasicInfoForm
)
from .models import UserProfile, PatientProfile, DoctorProfile, PATIENT, DOCTOR, ADMIN

def home(request):
    return render(request, 'accounts/home.html')

def register_choice(request):
    """View to choose between patient and doctor registration"""
    return render(request, 'accounts/register_choice.html')

def register_patient(request):
    """Patient registration view"""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Patient account successfully created! You can now log in.')
            return redirect('login')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/register_patient.html', {'form': form})

def register_doctor(request):
    """Doctor registration view"""
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Doctor account successfully created! Please wait for admin approval before logging in.')
            return redirect('login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'accounts/register_doctor.html', {'form': form})

def login_view(request):
    """Custom login view that redirects users based on their role"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            
            # Redirect based on user role
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.is_patient():
                    return redirect('patient_dashboard')
                elif profile.is_doctor():
                    return redirect('doctor_dashboard')
                elif profile.is_admin():
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            except UserProfile.DoesNotExist:
                # Fallback if profile doesn't exist
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Logout the user and redirect to home page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    user_profile = request.user.profile
    
    if user_profile.is_patient():
        return redirect('patient_dashboard')
    elif user_profile.is_doctor():
        return redirect('doctor_dashboard')
    elif user_profile.is_admin():
        return redirect('admin_dashboard')
    else:
        # Fallback for undefined roles
        return render(request, 'accounts/dashboard.html')

@login_required
def patient_dashboard(request):
    if not request.user.profile.is_patient():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Get data for patient dashboard
    try:
        patient_profile = request.user.patient_profile
        appointments = request.user.patient_appointments.all()[:5]
        prescriptions = request.user.patient_prescriptions.filter(is_active=True)
        medical_records = request.user.medical_records.all()[:5]
        
        # Get all active medication reminders for all active prescriptions
        from prescriptions.models import MedicationReminder
        prescription_ids = prescriptions.values_list('id', flat=True)
        upcoming_reminders = MedicationReminder.objects.filter(prescription_id__in=prescription_ids, is_active=True).order_by('reminder_time')

        context = {
            'patient_profile': patient_profile,
            'appointments': appointments,
            'prescriptions': prescriptions,
            'medical_records': medical_records,
            'upcoming_reminders': upcoming_reminders,
        }
    except:
        # Handle case where patient_profile doesn't exist yet
        context = {}
    
    return render(request, 'accounts/patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if not request.user.profile.is_doctor():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Get current date for comparing with appointments
    today = date.today()
    
    # Get data for doctor dashboard
    try:
        doctor_profile = request.user.doctor_profile
        appointments = request.user.doctor_appointments.all()
        
        # Filter appointments for today and pending status
        todays_appointments = [apt for apt in appointments if apt.appointment_date == today]
        pending_appointments = [apt for apt in appointments if apt.status == 'pending']
        pending_appointments_count = len(pending_appointments)
        
        # Get recent patient records
        patient_records = request.user.patient_records.all()[:5]
        
        context = {
            'doctor_profile': doctor_profile,
            'appointments': appointments[:5],
            'todays_appointments': todays_appointments,
            'pending_appointments': pending_appointments,
            'pending_appointments_count': pending_appointments_count,
            'patient_records': patient_records,
            'today': today,
        }
    except Exception as e:
        # Handle case where doctor_profile doesn't exist yet
        context = {'today': today, 'error': str(e)}
    
    return render(request, 'accounts/doctor_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.profile.is_admin():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Get data for admin dashboard
    users = User.objects.all()[:10]
    patients = User.objects.filter(profile__role=PATIENT)[:5]
    doctors = User.objects.filter(profile__role=DOCTOR)[:5]
    
    context = {
        'users': users,
        'patients': patients,
        'doctors': doctors,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def profile(request):
    user_profile = request.user.profile
    
    if request.method == 'POST':
        # Update basic user info
        user_form = UserBasicInfoForm(request.POST, instance=request.user)
        # Update common profile info
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        # Get the appropriate specific profile form based on user role
        if user_profile.is_patient():
            try:
                patient_profile = request.user.patient_profile
            except PatientProfile.DoesNotExist:
                patient_profile = PatientProfile.objects.create(user=request.user)
            specific_form = PatientProfileForm(request.POST, instance=patient_profile)
        elif user_profile.is_doctor():
            try:
                doctor_profile = request.user.doctor_profile
            except DoctorProfile.DoesNotExist:
                doctor_profile = DoctorProfile.objects.create(user=request.user)
            specific_form = DoctorProfileForm(request.POST, instance=doctor_profile)
        else:
            specific_form = None
        
        # Check if all forms are valid
        forms_valid = user_form.is_valid() and profile_form.is_valid()
        if specific_form is not None:
            forms_valid = forms_valid and specific_form.is_valid()
        
        if forms_valid:
            user_form.save()
            profile_form.save()
            if specific_form is not None:
                specific_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        # Initialize forms
        user_form = UserBasicInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
        
        # Get the appropriate specific profile form based on user role
        if user_profile.is_patient():
            try:
                patient_profile = request.user.patient_profile
            except PatientProfile.DoesNotExist:
                patient_profile = PatientProfile.objects.create(user=request.user)
            specific_form = PatientProfileForm(instance=patient_profile)
        elif user_profile.is_doctor():
            try:
                doctor_profile = request.user.doctor_profile
            except DoctorProfile.DoesNotExist:
                doctor_profile = DoctorProfile.objects.create(user=request.user)
            specific_form = DoctorProfileForm(instance=doctor_profile)
        else:
            specific_form = None
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'specific_form': specific_form,
        'user_profile': user_profile
    }
    
    return render(request, 'accounts/profile.html', context)
