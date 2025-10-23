from django.urls import path
from django import views
from django.urls import path


from review.views import show_review_lapangan
from review.views import add_review_lapangan, delete_review, get_reviews_json, get_single_review_json, show_edit_review_lapangan, show_feeds_review_lapangan, show_form_review_lapangan, update_review


# app_name = 'review'

from review.views import show_review_lapangan
from review.views import add_review_lapangan, delete_review, get_reviews_json, get_single_review_json, show_edit_review_lapangan, show_feeds_review_lapangan, show_form_review_lapangan, update_review

app_name = 'review'

urlpatterns = [    
    path('lapangan/review/<uuid:lapangan_id>/', show_review_lapangan, name='show_review_lapangan'),
    path('lapangan/review/add-ajax/<uuid:lapangan_id>/', add_review_lapangan, name='add_review_lapangan'),
    path('lapangan/review/json/<uuid:lapangan_id>/', get_reviews_json, name='get_reviews_json'),
    path('lapangan/review/delete-ajax/<int:review_id>/', delete_review, name='delete_review'),
    path('lapangan/review/feeds/<uuid:lapangan_id>/', show_feeds_review_lapangan, name='show_feeds_review_lapangan'),
    path('lapangan/review/form/<uuid:lapangan_id>/', show_form_review_lapangan, name='show_form_review_lapangan'),
    path('lapangan/review/update-ajax/<int:review_id>/', update_review, name='update_review'),
    path('json/review/<int:review_id>/', get_single_review_json, name='get_single_review_json'),
    path('lapangan/review/edit/<int:review_id>/', show_edit_review_lapangan, name='show_edit_review_lapangan'),
    path('<int:coach_id>/', views.show_feeds_review_coach, name='show_feeds_review_coach'),
    path('<int:coach_id>/add/', views.show_form_review_coach, name='show_form_review_coach'),
    path('edit/<int:review_id>/', views.edit_review_coach, name='edit_review_coach'),
    path('delete/<int:review_id>/', views.delete_review_coach, name='delete_review_coach'),
    path('json/<int:coach_id>/', views.get_reviews_json, name='get_reviews_json'),
]