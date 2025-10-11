from django.urls import path
from main.views import show_main, login_user, register, logout_user
from main.views import register_ajax, login_ajax, logout_ajax, show_profile, update_profile_ajax
app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('login/', login_user, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('register-ajax/', register_ajax, name='register_ajax'),
    path('login-ajax/', login_ajax, name='login_ajax'),
    path('logout-ajax/', logout_ajax, name='logout_ajax'),
    path('profile/', show_profile, name='show_profile'),
    path('profile/update/', update_profile_ajax, name='update_profile_ajax'),
]