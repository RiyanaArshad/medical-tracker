from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserProfile

class MedicalRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records', limit_choices_to={'profile__role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patient_records', limit_choices_to={'profile__role': 'doctor'})
    diagnosis = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.diagnosis} - {self.date_created.strftime('%Y-%m-%d')}"

class MedicalReport(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50)  # e.g., X-ray, Blood Test, etc.
    date = models.DateField()
    report_file = models.FileField(upload_to='medical_reports/')
    notes = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_reports')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.medical_record.patient.username} - {self.date}"
