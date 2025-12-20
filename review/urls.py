# review/urls.py
from django.urls import include, path
from . import views
from review import views as review_views
from django.views.decorators.csrf import csrf_exempt

app_name = 'review'

urlpatterns = [
    # =================== REVIEW LAPANGAN ===================
    path(
        'lapangan/<uuid:lapangan_id>/',
        views.show_review_lapangan,
        name='show_review_lapangan',
    ),
    path(
        'lapangan/add-ajax/<uuid:lapangan_id>/',
        views.add_review_lapangan,
        name='add_review_lapangan',
    ),
    path(
        'lapangan/json/<uuid:lapangan_id>/',
        views.get_reviews_json_lapangan,
        name='get_reviews_json_lapangan',
    ),
    path(
        'lapangan/delete-ajax/<int:review_id>/',
        views.delete_review,
        name='delete_review',
    ),
    path(
        'lapangan/feeds/<uuid:lapangan_id>/',
        views.show_feeds_review_lapangan,
        name='show_feeds_review_lapangan',
    ),
    path(
        'lapangan/form/<uuid:lapangan_id>/',
        views.show_form_review_lapangan,
        name='show_form_review_lapangan',
    ),
    path(
        'lapangan/update-ajax/<int:review_id>/',
        views.update_review,
        name='update_review',
    ),
    path(
        'lapangan/json-single/<int:review_id>/',
        views.get_single_review_json,
        name='get_single_review_json',
    ),
    path(
        'lapangan/edit/<int:review_id>/',
        views.show_edit_review_lapangan,
        name='show_edit_review_lapangan',
    ),
    path(
        'lapangan/<int:lapangan_id>/reviews/',
        views.get_reviews_json_lapangan,
        name='reviews-lapangan',
    ),
# ====== REVIEW COACH (WEB + FLUTTER) ======
    path('coach/<int:coach_id>/', review_views.show_feeds_review_coach,
         name='show_feeds_review_coach'),
    path('coach/<int:coach_id>/add/', review_views.show_form_review_coach,
         name='show_form_review_coach'),

    # halaman edit (HTML)
    path('coach/edit/<int:review_id>/', review_views.edit_review_coach,
         name='edit_review_coach'),

    # hapus (JSON, sudah kamu pakai dan OK)
    path('coach/delete/<int:review_id>/', review_views.delete_review_coach,
         name='delete_review_coach'),

    # JSON list review coach (ini yang dipakai Flutter buat fetch)
    path('coach/json/<int:coach_id>/', review_views.get_reviews_json,
         name='get_reviews_json_coach'),

    # endpoint AJAX khusus Flutter
    path('coach/add-ajax/<int:coach_id>/',
         csrf_exempt(review_views.add_review_coach_ajax),
         name='add_review_coach_ajax'),

    # endpoint update review khusus Flutter
    path('coach/edit-ajax/<int:review_id>/',
         review_views.edit_review_coach_ajax,
         name='edit_review_coach_ajax'),
]
