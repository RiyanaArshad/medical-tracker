from django.db import models
from django.contrib.auth.models import User
from medical_records.models import MedicalRecord

FREQUENCY_CHOICES = (
    ('once_daily', 'Once Daily'),
    ('twice_daily', 'Twice Daily'),
    ('thrice_daily', 'Three Times a Day'),
    ('four_times_daily', 'Four Times a Day'),
    ('as_needed', 'As Needed'),
    ('custom', 'Custom')
)

class Prescription(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_prescriptions', limit_choices_to={'profile__role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_prescriptions', limit_choices_to={'profile__role': 'doctor'})
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    
    date_prescribed = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    custom_frequency = models.CharField(max_length=255, blank=True, null=True)
    
    instructions = models.TextField()
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.medication_name} - {self.date_prescribed}"
    
    def needs_refill(self):
        # Logic to determine if medication needs a refill
        return False

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
class MedicationReminder(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.prescription.medication_name} - {self.reminder_time}"
