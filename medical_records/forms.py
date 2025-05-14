from django import forms
from .models import MedicalRecord, MedicalReport

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient', 'diagnosis', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        
        # If this is a doctor creating the record
        if self.doctor:
            # Get only patients (filter by role)
            self.fields['patient'].queryset = self.fields['patient'].queryset.filter(profile__role='patient')
    
    def save(self, commit=True):
        medical_record = super().save(commit=False)
        if self.doctor:
            medical_record.doctor = self.doctor
        if commit:
            medical_record.save()
        return medical_record

class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['title', 'report_type', 'date', 'report_file', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.medical_record = kwargs.pop('medical_record', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        report = super().save(commit=False)
        if self.medical_record:
            report.medical_record = self.medical_record
        if self.user:
            report.uploaded_by = self.user
        if commit:
            report.save()
        return report 