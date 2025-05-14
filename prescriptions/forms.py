from django import forms
from django.contrib.auth.models import User
from .models import Prescription, MedicationReminder, FREQUENCY_CHOICES

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'medical_record', 'start_date', 'end_date', 
                 'medication_name', 'dosage', 'frequency', 'custom_frequency', 'instructions', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'medication_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'custom_frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'medical_record': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        
        # Filter patient field to show only patients
        self.fields['patient'].queryset = User.objects.filter(profile__role='patient')
        self.fields['patient'].widget.attrs.update({'class': 'form-control'})
        
        # Set custom_frequency field to be not required
        self.fields['custom_frequency'].required = False
        
        # If a specific patient is selected, filter medical records
        patient_id = None
        if self.data.get('patient'):
            patient_id = self.data.get('patient')
        elif 'patient' in self.initial:
            patient_id = self.initial['patient']
        elif self.instance and self.instance.patient_id:
            patient_id = self.instance.patient_id
            
        if patient_id:
            self.fields['medical_record'].queryset = self.fields['medical_record'].queryset.filter(patient_id=patient_id)
        else:
            self.fields['medical_record'].queryset = self.fields['medical_record'].queryset.none()
        
        self.fields['medical_record'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        prescription = super().save(commit=False)
        if self.doctor:
            prescription.doctor = self.doctor
            # Also set the doctor as the last updater
            prescription.last_updated_by = self.doctor
        if commit:
            prescription.save()
        return prescription

REMINDER_TIME_CHOICES = [
    ("06:00", "Morning (6:00 AM)"),
    ("12:00", "Noon (12:00 PM)"),
    ("15:00", "Afternoon (3:00 PM)"),
    ("18:00", "Evening (6:00 PM)"),
    ("21:00", "Night (9:00 PM)")
]

class MedicationReminderForm(forms.ModelForm):
    reminder_time = forms.ChoiceField(choices=REMINDER_TIME_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label="Reminder Time")
    is_active = forms.BooleanField(initial=True, required=False, label="Active")
    class Meta:
        model = MedicationReminder
        fields = ['reminder_time', 'is_active']
    
    def __init__(self, *args, **kwargs):
        self.prescription = kwargs.pop('prescription', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        reminder = super().save(commit=False)
        if self.prescription:
            reminder.prescription = self.prescription
        if commit:
            reminder.save()
        return reminder 