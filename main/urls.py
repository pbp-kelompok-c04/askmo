from django.urls import include, path
from review.views import add_review_lapangan, delete_review, get_reviews_json, get_reviews_json_lapangan, get_single_review_json, show_edit_review_lapangan, show_feeds_review_lapangan, show_form_review_lapangan, show_review_lapangan, update_review
from main.views import login_user, logout_user, register, register_ajax, login_ajax, logout_ajax, show_main
from django.urls import path
from main.views import show_main, login_user, register, logout_user
from main.views import register_ajax, login_ajax, logout_ajax, show_profile, update_profile_ajax
from . import views


from main.views import show_xml, show_json, show_xml_by_id, show_json_by_id, show_lapangan_by_alamat_xml, show_lapangan_by_alamat_json, show_lapangan_by_kecamatan_xml, show_lapangan_by_kecamatan_json, show_lapangan_dashboard


from main.views import add_event_ajax, show_main, login_user, register, logout_user
from main.views import register_ajax, login_ajax, logout_ajax, show_profile, update_profile_ajax, delete_event_ajax
from main.views import show_event, show_event_detail, get_events_json, get_event_detail_ajax, edit_event_ajax
from review.views import show_feeds_review_coach
from review import views as review_views
app_name = 'main'


urlpatterns = [
    path('', show_main, name='show_main'),
    path('login/', login_user, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('register-ajax/', register_ajax, name='register_ajax'),
    path('login-ajax/', login_ajax, name='login_ajax'),
    path('logout-ajax/', logout_ajax, name='logout_ajax'),
   
    # === LAPANGAN & JSON/XML ===
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<uuid:lapangan_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<uuid:lapangan_id>/', show_json_by_id, name='show_json_by_id'),
    path('xml/alamat/<str:alamat>/', show_lapangan_by_alamat_xml, name='show_lapangan_by_alamat_xml'),
    path('json/alamat/<str:alamat>/', show_lapangan_by_alamat_json, name='show_lapangan_by_alamat_json'),
    path('xml/kecamatan/<str:kecamatan>/', show_lapangan_by_kecamatan_xml, name='show_lapangan_by_kecamatan_xml'),
    path('json/kecamatan/<str:kecamatan>/', show_lapangan_by_kecamatan_json, name='show_lapangan_by_kecamatan_json'),
    path('lapangan/', show_lapangan_dashboard, name='show_lapangan_dashboard'),
    #=============================================
    #=== REVIEW LAPANGAN & COACH ===
    #=============================================
    path('lapangan/review/<uuid:lapangan_id>/', show_review_lapangan, name='show_review_lapangan'),
    path('lapangan/review/add-ajax/<uuid:lapangan_id>/', add_review_lapangan, name='add_review_lapangan'),
    path('lapangan/review/json/<uuid:lapangan_id>/', get_reviews_json_lapangan, name='get_reviews_json_lapangan'),  # ⚠️ NAMA BARU
    path('lapangan/review/delete-ajax/<int:review_id>/', delete_review, name='delete_review'),
    path('lapangan/review/feeds/<uuid:lapangan_id>/', show_feeds_review_lapangan, name='show_feeds_review_lapangan'),
    path('lapangan/review/form/<uuid:lapangan_id>/', show_form_review_lapangan, name='show_form_review_lapangan'),
    path('lapangan/review/update-ajax/<int:review_id>/', update_review, name='update_review'),
    path('json/review/<int:review_id>/', get_single_review_json, name='get_single_review_json'),
    path('lapangan/review/edit/<int:review_id>/', show_edit_review_lapangan, name='show_edit_review_lapangan'),

    # === PROFILE ===
    path('profile/', show_profile, name='show_profile'),
    path('profile/update/', update_profile_ajax, name='update_profile_ajax'),
   
    # === WISHLIST / KOLEKSI ===
    # Wishlist Default: Arahkan ke daftar Lapangan
    path('wishlist/', views.show_wishlist_lapangan, name='show_user_collections'), # Digunakan sebagai default/link Lapangan di profile
    path('wishlist/lapangan/', views.show_wishlist_lapangan, name='lapangan_wishlist_list'),
    path('wishlist/coach/', views.show_wishlist_coach, name='coach_wishlist_list'),
   
    # URL AJAX
    path('api/wishlist/create/', views.create_collection_ajax, name='create_collection_ajax'),
    path('api/collections/status/<str:item_type>/<uuid:item_id>/', views.get_user_collections_for_item_ajax, name='get_collections_status_ajax'),
    path('api/wishlist/toggle-save/', views.toggle_save_item_to_collection_ajax, name='toggle_save_item_ajax'),
    path('wishlist/<uuid:collection_id>/', views.show_collection_detail, name='show_collection_detail'),
    path('api/wishlist/edit/', views.edit_collection_name_ajax, name='edit_collection_name_ajax'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
   
    # Coach Add (Mengarahkan ke modal/collections)
    path('coach/add_to_wishlist/<uuid:coach_id>/', views.add_to_coach_list, name='add_to_coach_list'),
    path('event/', show_event, name='show_event'),
    path('event/<uuid:id>/', show_event_detail, name='show_event_detail'),
   
    path('get-events-json/', get_events_json, name='get_events_json'), # <-- THIS IS THE REQUIRED URL
    path('add-event-ajax/', add_event_ajax, name='add_event_ajax'),
    path('delete-event-ajax/<uuid:id>/', delete_event_ajax, name='delete_event_ajax'),


    path('get-event-ajax/<uuid:id>/', get_event_detail_ajax, name='get_event_detail_ajax'),
    path('edit-event-ajax/<uuid:id>/', edit_event_ajax, name='edit_event_ajax'),
]
