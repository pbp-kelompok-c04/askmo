from django.urls import path
from main.views import add_review_lapangan, delete_review, get_reviews_json, get_single_review_json, show_edit_review_lapangan, show_feeds_review_lapangan, show_form_review_lapangan, show_main, login_user, register, logout_user, show_review_lapangan, update_review
from main.views import register_ajax, login_ajax, logout_ajax

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
    path('lapangan/', show_lapangan_dashboard, name='show_lapangan_dashboard'),
    path('lapangan/review/<uuid:lapangan_id>/', show_review_lapangan, name='show_review_lapangan'),
    path('lapangan/review/add-ajax/<uuid:lapangan_id>/', add_review_lapangan, name='add_review_lapangan'),
    path('lapangan/review/json/<uuid:lapangan_id>/', get_reviews_json, name='get_reviews_json'),
    path('lapangan/review/delete-ajax/<int:review_id>/', delete_review, name='delete_review'),
    path('lapangan/review/feeds/<uuid:lapangan_id>/', show_feeds_review_lapangan, name='show_feeds_review_lapangan'),
    path('lapangan/review/form/<uuid:lapangan_id>/', show_form_review_lapangan, name='show_form_review_lapangan'),
    path('lapangan/review/add-ajax/<uuid:lapangan_id>/', add_review_lapangan, name='add_review_lapangan'),
    path('lapangan/review/feeds/<uuid:lapangan_id>/', show_feeds_review_lapangan, name='show_feeds_review_lapangan'),
    path('lapangan/review/update-ajax/<int:review_id>/', update_review, name='update_review'),
    path('json/review/<int:review_id>/', get_single_review_json, name='get_single_review_json'),
    path('lapangan/review/edit/<int:review_id>/', show_edit_review_lapangan, name='show_edit_review_lapangan'),
]