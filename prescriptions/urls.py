from django.urls import path
from . import views

urlpatterns = [
    path('', views.prescription_list, name='prescription_list'),
    path('create/', views.prescription_create, name='prescription_create'),
    path('<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    path('<int:prescription_id>/update/', views.prescription_update, name='prescription_update'),
    path('<int:prescription_id>/reminder/add/', views.reminder_create, name='reminder_create'),
    path('reminder/<int:reminder_id>/update/', views.reminder_update, name='reminder_update'),
] 