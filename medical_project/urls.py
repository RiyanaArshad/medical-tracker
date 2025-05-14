"""
URL configuration for medical_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Account URLs
    path('', accounts_views.home, name='home'),
    path('register/', accounts_views.register_choice, name='register_choice'),
    path('register/patient/', accounts_views.register_patient, name='register_patient'),
    path('register/doctor/', accounts_views.register_doctor, name='register_doctor'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('dashboard/', accounts_views.dashboard, name='dashboard'),
    path('patient-dashboard/', accounts_views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', accounts_views.doctor_dashboard, name='doctor_dashboard'),
    path('admin-dashboard/', accounts_views.admin_dashboard, name='admin_dashboard'),
    path('profile/', accounts_views.profile, name='profile'),
    
    # App URLs
    path('medical-records/', include('medical_records.urls')),
    path('appointments/', include('appointments.urls')),
    path('prescriptions/', include('prescriptions.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
