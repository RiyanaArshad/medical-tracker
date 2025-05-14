from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from .models import Appointment, STATUS_CHOICES
from accounts.models import DoctorProfile
from difflib import get_close_matches

class AppointmentForm(forms.ModelForm):
    specialization = forms.ChoiceField(
        choices=[('', '---Select Specialization---')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select the type of doctor you need'
    )

    class Meta:
        model = Appointment
        fields = ['specialization', 'doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.now().date().isoformat()}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Please describe your reason for the appointment'}),
        }

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)

        # Populate specializations
        specializations = DoctorProfile.objects.values_list(
            'specialization', flat=True
        ).distinct()
        self.fields['specialization'].choices = [
            ('', '---Select Specialization---')
        ] + [(spec, spec) for spec in specializations]

        # Set doctor queryset based on selected specialization
        specialization = self.data.get('specialization') or self.initial.get('specialization')
        if specialization:
            self.fields['doctor'].queryset = User.objects.filter(
                profile__role='doctor',
                doctor_profile__specialization=specialization
            )
        else:
            self.fields['doctor'].queryset = User.objects.none()


    def clean_specialization(self):
        specialization = self.cleaned_data['specialization']
        if not DoctorProfile.objects.filter(specialization=specialization).exists():
            all_specs = DoctorProfile.objects.values_list('specialization', flat=True)
            suggestions = get_close_matches(specialization, all_specs, n=3, cutoff=0.6)
            if suggestions:
                raise forms.ValidationError(
                    f"Invalid specialization. Did you mean: {', '.join(suggestions)}?"
                )
            else:
                raise forms.ValidationError("Invalid specialization selected.")
        return specialization

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        specialization = cleaned_data.get('specialization')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        # Validate doctor matches specialization
        if doctor and specialization:
            if not hasattr(doctor, 'doctor_profile') or doctor.doctor_profile.specialization != specialization:
                self.add_error('doctor', 'Selected doctor does not match the specialization.')

        # Validate appointment datetime
        if appointment_date and appointment_time:
            appointment_datetime = timezone.make_aware(
                datetime.combine(appointment_date, appointment_time)
            )
            if appointment_datetime <= timezone.now():
                raise forms.ValidationError('Appointment must be scheduled in the future.')

        return cleaned_data

    def save(self, commit=True):
        appointment = super().save(commit=False)
        if self.patient:
            appointment.patient = self.patient
            appointment.status = 'pending'  # Set initial status
        if commit:
            appointment.save()
        return appointment

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'status', 'notes']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
