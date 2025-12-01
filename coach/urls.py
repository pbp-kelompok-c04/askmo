# coach/urls.py
from django.urls import include, path
from . import views

app_name = 'coach'

urlpatterns = [
    # URL untuk Halaman Publik
    path('', views.coach_list_view, name='coach_list'),
    
    # !!! PATH BARU UNTUK DETAIL COACH !!!
    path('<int:pk>/', views.coach_detail_view, name='coach_detail'),

    # URL untuk Panel Admin Kustom
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/create/', views.coach_create_view, name='coach_create'),
    path('dashboard/<int:pk>/update/', views.coach_update_view, name='coach_update'),
    path('dashboard/<int:pk>/delete/', views.coach_delete_view, name='coach_delete'),
    path('add-to-wishlist/<int:pk>/', views.add_to_wishlist_view, name='add_to_coach_list'),
    path('wishlist/', views.coach_wishlist_list_view, name='coach_wishlist_list'),
    path('coach_detail/<int:pk>/', views.coach_detail_view, name='coach_detail_view'),
    path('auth/', include('authentication.urls')),
    path('json/', views.show_json, name='show_json'),
    path('create-flutter/', views.create_coach_flutter, name='create_coach_flutter'),
    path('edit-coach-flutter/<int:pk>/', views.edit_coach_flutter, name='edit_coach_flutter'),
    path('delete-coach-ajax/<int:pk>/', views.delete_coach_flutter, name='delete_coach_flutter'),
]