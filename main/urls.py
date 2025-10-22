from django.urls import path
from main.views import add_event_ajax, show_main, login_user, register, logout_user
from main.views import register_ajax, login_ajax, logout_ajax, show_profile, update_profile_ajax, delete_event_ajax
from main.views import show_event, show_event_detail, get_events_json, get_event_detail_ajax, edit_event_ajax
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
    path('event/', show_event, name='show_event'),
    path('event/<uuid:id>/', show_event_detail, name='show_event_detail'),
    
    path('get-events-json/', get_events_json, name='get_events_json'), # <-- THIS IS THE REQUIRED URL
    path('add-event-ajax/', add_event_ajax, name='add_event_ajax'),
    path('delete-event-ajax/<uuid:id>/', delete_event_ajax, name='delete_event_ajax'),

    path('get-event-ajax/<uuid:id>/', get_event_detail_ajax, name='get_event_detail_ajax'),
    path('edit-event-ajax/<uuid:id>/', edit_event_ajax, name='edit_event_ajax'),
]