from django import views
from django.urls import include, path
from . import views

app_name = 'review'


urlpatterns = [    
    # REVIEW LAPANGAN
    path('lapangan/<uuid:lapangan_id>/', views.show_review_lapangan, name='show_review_lapangan'),
    path('lapangan/add-ajax/<uuid:lapangan_id>/', views.add_review_lapangan, name='add_review_lapangan'),
    path('lapangan/json/<uuid:lapangan_id>/', views.get_reviews_json_lapangan, name='get_reviews_json_lapangan'), 
    path('lapangan/delete-ajax/<int:review_id>/', views.delete_review, name='delete_review'),
    path('lapangan/feeds/<uuid:lapangan_id>/', views.show_feeds_review_lapangan, name='show_feeds_review_lapangan'),
    path('lapangan/form/<uuid:lapangan_id>/', views.show_form_review_lapangan, name='show_form_review_lapangan'),
    path('lapangan/update-ajax/<int:review_id>/', views.update_review, name='update_review'),
    path('lapangan/json-single/<int:review_id>/', views.get_single_review_json, name='get_single_review_json'),
    path('lapangan/edit/<int:review_id>/', views.show_edit_review_lapangan, name='show_edit_review_lapangan'),
    path('lapangan/<int:lapangan_id>/reviews/', views.get_reviews_json_lapangan, name='reviews-lapangan'),

    
    # REVIEW COACH
    path('coach/<int:coach_id>/', views.show_feeds_review_coach, name='show_feeds_review_coach'),
    path('coach/<int:coach_id>/add/', views.show_form_review_coach, name='show_form_review_coach'),
    path('coach/edit/<int:review_id>/', views.edit_review_coach, name='edit_review_coach'),
    path('coach/delete/<int:review_id>/', views.delete_review_coach, name='delete_review_coach'),
    path('coach/json/<int:coach_id>/', views.get_reviews_json, name='get_reviews_json_coach'), 

    path('auth/', include('authentication.urls')),
]
