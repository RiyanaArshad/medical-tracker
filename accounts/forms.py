from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, DoctorProfile, PatientProfile, DOCTOR, PATIENT, ADMIN

class BaseUserRegistrationForm(UserCreationForm):
    """Base registration form with common fields for all user types"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            user_profile = user.profile
            user_profile.phone_number = self.cleaned_data['phone_number']
            user_profile.address = self.cleaned_data['address']
            if 'profile_picture' in self.cleaned_data and self.cleaned_data['profile_picture']:
                user_profile.profile_picture = self.cleaned_data['profile_picture']
            user_profile.save()
            
        return user

class PatientRegistrationForm(BaseUserRegistrationForm):
    """Registration form specific for patients"""
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    blood_group = forms.ChoiceField(choices=PatientProfile.BLOOD_GROUP_CHOICES, required=False)
    allergies = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    chronic_conditions = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_number = forms.CharField(max_length=15, required=False)
    emergency_contact_relationship = forms.CharField(max_length=50, required=False)
    insurance_provider = forms.CharField(max_length=100, required=False)
    insurance_policy_number = forms.CharField(max_length=50, required=False)
    
    def save(self, commit=True):
        user = super().save(commit)
        user.profile.role = PATIENT
        user.profile.save()
        
        if commit:
            patient_profile, created = PatientProfile.objects.get_or_create(user=user)
            patient_profile.date_of_birth = self.cleaned_data['date_of_birth']
            patient_profile.blood_group = self.cleaned_data['blood_group']
            patient_profile.allergies = self.cleaned_data['allergies']
            patient_profile.chronic_conditions = self.cleaned_data['chronic_conditions']
            patient_profile.emergency_contact_name = self.cleaned_data['emergency_contact_name']
            patient_profile.emergency_contact_number = self.cleaned_data['emergency_contact_number']
            patient_profile.emergency_contact_relationship = self.cleaned_data['emergency_contact_relationship']
            patient_profile.insurance_provider = self.cleaned_data['insurance_provider']
            patient_profile.insurance_policy_number = self.cleaned_data['insurance_policy_number']
            patient_profile.save()
            
        return user

class DoctorRegistrationForm(BaseUserRegistrationForm):
    """Registration form specific for doctors"""
    specialization = forms.CharField(max_length=100, required=True)
    license_number = forms.CharField(max_length=50, required=True)
    years_of_experience = forms.IntegerField(min_value=0, required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    available_days = forms.CharField(max_length=100, required=False, 
                                   help_text="E.g., Mon,Tue,Wed")
    available_times = forms.CharField(max_length=100, required=False,
                                    help_text="E.g., 9:00-13:00,15:00-18:00")
    education = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    def save(self, commit=True):
        user = super().save(commit)
        user.profile.role = DOCTOR
        user.profile.save()
        
        if commit:
            doctor_profile, created = DoctorProfile.objects.get_or_create(user=user)
            doctor_profile.specialization = self.cleaned_data['specialization']
            doctor_profile.license_number = self.cleaned_data['license_number']
            doctor_profile.years_of_experience = self.cleaned_data.get('years_of_experience') or 0
            doctor_profile.bio = self.cleaned_data['bio']
            doctor_profile.consultation_fee = self.cleaned_data.get('consultation_fee') or 0
            doctor_profile.available_days = self.cleaned_data['available_days']
            doctor_profile.available_times = self.cleaned_data['available_times']
            doctor_profile.education = self.cleaned_data['education']
            doctor_profile.save()
            
        return user

class PatientProfileForm(forms.ModelForm):
    """Form for updating patient profile"""
    class Meta:
        model = PatientProfile
        exclude = ('user',)
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'allergies': forms.Textarea(attrs={'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 2}),
        }

class DoctorProfileForm(forms.ModelForm):
    """Form for updating doctor profile"""
    class Meta:
        model = DoctorProfile
        exclude = ('user',)
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'education': forms.Textarea(attrs={'rows': 3}),
        }

class UserProfileForm(forms.ModelForm):
    """Form for updating common user profile fields"""
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'profile_picture')

class UserBasicInfoForm(forms.ModelForm):
    """Form for updating basic user information"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email') 