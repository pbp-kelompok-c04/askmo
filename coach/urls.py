# coach/urls.py
from django.urls import path
from . import views

app_name = 'coach'

urlpatterns = [
    # --- Public Views ---
    path('', views.coach_list_view, name='coach_list'),
    
    # --- Admin Authentication Views ---
    path('management/login/', views.login_view, name='login'),
    path('management/logout/', views.logout_view, name='logout'),

    # --- Admin CRUD Views ---
    path('management/dashboard/', views.dashboard_view, name='dashboard'),
    path('management/coach/add/', views.coach_create_view, name='coach_create'),
    path('management/coach/edit/<int:pk>/', views.coach_update_view, name='coach_update'),
    path('management/coach/delete/<int:pk>/', views.coach_delete_view, name='coach_delete'),
]