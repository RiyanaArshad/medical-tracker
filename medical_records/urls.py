from django.urls import path
from . import views

urlpatterns = [
    path('', views.medical_record_list, name='medical_record_list'),
    path('create/', views.medical_record_create, name='medical_record_create'),
    path('<int:record_id>/', views.medical_record_detail, name='medical_record_detail'),
    path('<int:record_id>/update/', views.medical_record_update, name='medical_record_update'),
    path('<int:record_id>/report/create/', views.medical_report_create, name='medical_report_create'),
    path('report/<int:report_id>/', views.medical_report_detail, name='medical_report_detail'),
    path('report/<int:report_id>/download/', views.report_download, name='report_download'),
    path('report/<int:report_id>/view/', views.report_view, name='report_view'),
]