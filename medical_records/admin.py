from django.contrib import admin
from .models import MedicalRecord, MedicalReport

class MedicalReportInline(admin.TabularInline):
    model = MedicalReport
    extra = 0

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'date_created', 'date_updated')
    list_filter = ('date_created', 'doctor')
    search_fields = ('patient__username', 'doctor__username', 'diagnosis')
    inlines = [MedicalReportInline]

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'medical_record', 'report_type', 'date', 'uploaded_by', 'date_uploaded')
    list_filter = ('report_type', 'date', 'date_uploaded')
    search_fields = ('title', 'medical_record__patient__username', 'report_type')
