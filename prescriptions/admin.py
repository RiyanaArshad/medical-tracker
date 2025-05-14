from django.contrib import admin
from .models import Prescription, MedicationReminder

class MedicationReminderInline(admin.TabularInline):
    model = MedicationReminder
    extra = 0

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'medication_name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'frequency', 'doctor')
    search_fields = ('patient__username', 'doctor__username', 'medication_name')
    inlines = [MedicationReminderInline]

@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'reminder_time', 'is_active')
    list_filter = ('is_active', 'reminder_time')
    search_fields = ('prescription__medication_name', 'prescription__patient__username')
