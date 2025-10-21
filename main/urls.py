from django.urls import path
from main.views import show_main, login_user, register, logout_user
from main.views import register_ajax, login_ajax, logout_ajax, show_profile, update_profile_ajax
from . import views

from main.views import show_xml, show_json, show_xml_by_id, show_json_by_id, show_lapangan_by_alamat_xml, show_lapangan_by_alamat_json,  show_lapangan_by_kecamatan_xml, show_lapangan_by_kecamatan_json, show_lapangan_dashboard
app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('login/', login_user, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('register-ajax/', register_ajax, name='register_ajax'),
    path('login-ajax/', login_ajax, name='login_ajax'),
    path('logout-ajax/', logout_ajax, name='logout_ajax'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<uuid:lapangan_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<uuid:lapangan_id>/', show_json_by_id, name='show_json_by_id'),
    path('xml/alamat/<str:alamat>/', show_lapangan_by_alamat_xml, name='show_lapangan_by_alamat_xml'),
    path('json/alamat/<str:alamat>/', show_lapangan_by_alamat_json, name='show_lapangan_by_alamat_json'),
    path('xml/kecamatan/<str:kecamatan>/', show_lapangan_by_kecamatan_xml, name='show_lapangan_by_kecamatan_xml'),
    path('json/kecamatan/<str:kecamatan>/', show_lapangan_by_kecamatan_json, name='show_lapangan_by_kecamatan_json'),
    path('profile/', show_profile, name='show_profile'),
    path('profile/update/', update_profile_ajax, name='update_profile_ajax'),
    path('lapangan/', show_lapangan_dashboard, name='show_lapangan_dashboard'),
    path('wishlist/', views.show_user_collections, name='show_user_collections'),
    path('wishlist/lapangan/', views.show_wishlist_lapangan, name='lapangan_wishlist_list'),
    path('api/wishlist/create/', views.create_collection_ajax, name='create_collection_ajax'),
    path('wishlist/coach/', views.show_user_collections, name='coach_wishlist_list'),
    path('profile/', show_profile, name='show_profile'),
    path('profile/update/', update_profile_ajax, name='update_profile_ajax'),
    path('api/collections/status/<str:item_type>/<uuid:item_id>/', views.get_user_collections_for_item_ajax, name='get_collections_status_ajax'),
    path('api/wishlist/toggle-save/', views.toggle_save_item_to_collection_ajax, name='toggle_save_item_ajax'),
    path('wishlist/<uuid:collection_id>/', views.show_collection_detail, name='show_collection_detail'),
    path('api/wishlist/edit/', views.edit_collection_name_ajax, name='edit_collection_name_ajax'),
    path('coach/add_to_wishlist/<uuid:coach_id>/', views.add_to_coach_list, name='add_to_coach_list'),
]