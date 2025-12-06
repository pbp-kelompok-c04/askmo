from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Avg


from main.forms import ReviewCoachForm, ReviewForm
from main.models import Lapangan
from review.models import Review, ReviewCoach


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers


from main import models
from main.forms import LapanganForm, CoachForm, EventForm
from main.models import Lapangan, Coach, Event
from django.db.models import Q


from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse


import datetime
import json
import uuid
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags;



from coach.models import Coach  # 
from .models import ReviewCoach
from .models import ReviewCoach
from coach.models import Coach  


#=================================================================================================
#===================================REVIW BUAT LAPANGAN=============================================
#===================================================================================================

#============= MUNCULIN FITUR REVIEW LAPANGAN =============
def show_review_lapangan(request, lapangan_id):
    # dia bakal nyari id lapangannya
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)
       
    # ngeproses ambil review per id lapangan itu
    reviews = Review.objects.filter(lapangan=lapangan)
    # nyediain review kosong juga buat add yang baru
    review_form = ReviewForm()


    context = {
        'lapangan': lapangan,
        'reviews': reviews,
        'review_form': review_form,
        'is_authenticated': request.user.is_authenticated
    }
    # ngirim semua datanya ke html
    return render(request, 'review/lapangan/review_lapangan.html', context)

#============= NAMPILIN SEMUA REVIEW LAPANGAN =============
def show_feeds_review_lapangan(request, lapangan_id):
    #ngambil lapangan by id dan rviewnya juga
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)
    
    #kalkulasi reviewnya
    reviews = Review.objects.filter(lapangan=lapangan).order_by('-tanggal_dibuat')
    total_reviews = reviews.count()

    if total_reviews > 0:
        average_rating = update_lapangan_rating(lapangan)
    else:
        average_rating = lapangan.original_rating
 
    context = {
        'lapangan': lapangan,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
    }
    #kirim semua datanya ke html
    return render(request, 'review/lapangan/feeds_review_lapangan.html', context)

#============= MENAMPILKAN FORM TAMBAH REVIEW LAPANGAN =============
#============= MENAMPILKAN FORM TAMBAH REVIEW LAPANGAN =============
def show_form_review_lapangan(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)

    #Handle POST request: validasi form, simpan review, update rating, redirect
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.lapangan = lapangan
            
            # ========= PERBAIKAN: JANGAN GANTI reviewer_name DENGAN USERNAME =========
            if request.user.is_authenticated:
                new_review.user = request.user
                # HANYA set reviewer_name ke username jika formnya kosong
                if not new_review.reviewer_name: 
                    new_review.reviewer_name = request.user.username
            else:
                # Untuk user anonymous, gunakan session key
                if not request.session.session_key:
                    request.session.create()
                new_review.session_key = request.session.session_key
                # Untuk anonymous, pastikan ada nama reviewer
                if not new_review.reviewer_name:
                    new_review.reviewer_name = "Anonim"
            
            new_review.save()
           
           # ini ngehubungin review dengan lapangan yang dituju sebelum disimpan
            update_lapangan_rating(lapangan)
           
            return redirect('main:show_feeds_review_lapangan', lapangan_id=lapangan.id)
    else:
        form = ReviewForm()


    context = {
        'lapangan': lapangan,
        'review_form': form,
    }
    return render(request, 'review/lapangan/form_review_lapangan.html', context)

#============= NGAMBIL DATA SINGLE REVIEW (JSON) =============
def get_single_review_json(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
        data = {
            'id': review.id,
            'reviewer_name': review.reviewer_name,
            'rating': float(review.rating),
            'review_text': review.review_text,
            'gambar': review.gambar,
            'can_edit': review.can_edit(request.user, request.session.session_key),
            'can_delete': review.can_delete(request.user, request.session.session_key),
        }
        return JsonResponse(data)
    except Review.DoesNotExist:
        return JsonResponse({'detail': 'Review not found'}, status=404)

#============= INI FUNGSI MUNCULLIN FORM EDIT REVIEW LAPANGAN =============
def show_edit_review_lapangan(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)

        # pakai helper di model, bukan cek manual
        can_edit = review.can_edit(request.user, request.session.session_key)
        if not can_edit:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk mengedit review ini.")

        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                update_lapangan_rating(review.lapangan)
                return redirect('main:show_feeds_review_lapangan', lapangan_id=review.lapangan.id)
        else:
            form = ReviewForm(instance=review)

        context = {
            'review': review,
            'review_form': form,
        }
        return render(request, 'review/lapangan/edit_review_lapangan.html', context)

    except Review.DoesNotExist:
        return HttpResponse("Review tidak ditemukan.", status=404)
    
#============= TAMBAH REVIEW LAPANGAN VIA AJAX =============
@csrf_exempt
def add_review_lapangan(request, lapangan_id):
    if request.method == 'POST':
        try:
            lapangan = Lapangan.objects.get(pk=lapangan_id)
        except Lapangan.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Lapangan tidak ditemukan.'}, status=404)
           
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.lapangan = lapangan
            
            if request.user.is_authenticated:
                new_review.user = request.user
                if not new_review.reviewer_name:  
                    new_review.reviewer_name = request.user.username
            else:
                if not request.session.session_key:
                    request.session.create()
                new_review.session_key = request.session.session_key
                if not new_review.reviewer_name:
                    new_review.reviewer_name = "Anonim"
            
            new_review.save()
           
            update_lapangan_rating(lapangan)
           
            return JsonResponse({
                'status': 'success', 
                'message': 'Review berhasil ditambahkan!',
                'review_id': new_review.id
            }, status=201)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
   
    return JsonResponse({'status': 'error', 'message': 'Metode permintaan tidak valid.'}, status=405)

#============= FUNGSI UPDATE RATING LAPANGAN =============
def update_lapangan_rating(lapangan):
    new_reviews = Review.objects.filter(lapangan=lapangan)
   
    # kalo gak ada review baru, ya pake yang original rating awal
    if new_reviews.count() == 0:
        lapangan.rating = lapangan.original_rating
        lapangan.save()
        return lapangan.rating
   
    # rating awal diitung sebagai satu kesatuan
    total_rating = lapangan.original_rating
    total_reviews = 1
   #kalkulasu rating
    for review in new_reviews:
        total_rating += float(review.rating)
        total_reviews += 1
   
    new_rating = round(total_rating / total_reviews, 1)
    lapangan.rating = new_rating
    lapangan.save()
   
    return new_rating

#============= MENDAPATKAN SEMUA REVIEW LAPANGAN (JSON) =============
def get_reviews_json_lapangan(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return JsonResponse({'detail': 'Lapangan not found'}, status=404)

    reviews_from_model = Review.objects.filter(
        lapangan=lapangan
    ).order_by('-tanggal_dibuat')

    all_reviews = []

    # 1. SELALU tambahkan 1 entry dataset (original_rating)
    all_reviews.append({
        'id': 0,
        'reviewer_name': 'Rating awal',
        'rating': float(lapangan.original_rating),  
        'review_text': lapangan.review or '',
        'tanggal_dibuat': 'Data Awal',
        'gambar': None,
        'gambar_url': None,
        'can_edit': False,
        'can_delete': False,
        'is_dataset': True,
        'is_own_review': False,
    })

    # 2. Tambahkan review user biasa
    for review in reviews_from_model:
        gambar_url = None
        if review.gambar:
            if hasattr(review.gambar, 'url'):
                gambar_url = review.gambar.url
            else:
                gambar_url = str(review.gambar)

        can_edit = review.can_edit(request.user, request.session.session_key)
        can_delete = review.can_delete(request.user, request.session.session_key)

        all_reviews.append({
            'id': review.id,
            'reviewer_name': review.reviewer_name or 'Anonymous',
            'rating': float(review.rating),
            'review_text': review.review_text or '',
            'tanggal_dibuat': review.tanggal_dibuat.strftime("%Y-%m-%d %H:%M"),
            'gambar': review.gambar,
            'gambar_url': gambar_url,
            'can_edit': can_edit,
            'can_delete': can_delete,
            'is_dataset': False,
            'is_own_review': can_edit,
        })

    return JsonResponse(all_reviews, safe=False)


#============= UPDATE REVIEW LAPANGAN VIA AJAX =============
@csrf_exempt
def update_review(request, review_id):
    if request.method == 'POST':
        try:
            review = Review.objects.get(pk=review_id)
            
            if not review.can_edit(request.user, request.session.session_key):
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Anda tidak memiliki izin untuk mengedit review ini.'
                }, status=403)
            
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                update_lapangan_rating(review.lapangan)
                return JsonResponse({'status': 'success', 'message': 'Review berhasil diupdate!'})
            else:
                errors = dict(form.errors.items())
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
               
        except Review.DoesNotExist: 
            return JsonResponse({'status': 'error', 'message': 'Review tidak ditemukan.'}, status=404)

#============= HAPUS REVIEW LAPANGAN VIA AJAX =============
@csrf_exempt
@require_POST
def delete_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
        
        if not review.can_delete(request.user, request.session.session_key):
            return JsonResponse({
                'status': 'error', 
                'message': 'Anda tidak memiliki izin untuk menghapus review ini.'
            }, status=403)
        
        lapangan = review.lapangan
        review.delete()
        update_lapangan_rating(lapangan)
        return JsonResponse({'status': 'success', 'message': 'Review berhasil dihapus.'}, status=200)
    except Review.DoesNotExist: 
        return JsonResponse({'status': 'error', 'message': 'Review tidak ditemukan.'}, status=404)
#=================================================================================================
#====================================REVIW BUAT COACH=============================================
#===================================================================================================

from django.db.models import Avg

def show_feeds_review_coach(request, coach_id):
    coach = get_object_or_404(Coach, pk=coach_id)

    reviews = coach.reviews.all()
    total_reviews = reviews.count()

    if total_reviews > 0:
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        average_rating = round(float(average_rating), 1) if average_rating is not None else None
    else:
        average_rating = None

    context = {
        'coach': coach,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
    }

    return render(request, 'review/coach/feeds_review_coach.html', context)


def show_form_review_coach(request, coach_id):
    coach = get_object_or_404(Coach, pk=coach_id)

    if request.method == 'POST':
        form = ReviewCoachForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.coach = coach
            review.user = request.user if request.user.is_authenticated else None
            if not review.user and not form.cleaned_data.get('reviewer_name'):
                review.reviewer_name = "Anonim"
            elif review.user and not form.cleaned_data.get('reviewer_name'):
                review.reviewer_name = request.user.username
            review.save()

            return redirect('main:show_feeds_review_coach', coach_id=coach_id)
    else:
        form = ReviewCoachForm()

    context = {
        'coach': coach,
        'review_form': form,
    }
    return render(request, 'review/coach/form_review_coach.html', context)


@login_required
def edit_review_coach(request, review_id):
    review = get_object_or_404(ReviewCoach, pk=review_id)

    if not review.can_edit(request.user):  # pakai helper
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengedit review ini.")

    if request.method == 'POST':
        form = ReviewCoachForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('main:show_feeds_review_coach', coach_id=review.coach.id)
    else:
        form = ReviewCoachForm(instance=review)

    context = {
        'review': review,
        'review_form': form,
    }
    return render(request, 'review/coach/edit_review_coach.html', context)


@require_POST
@csrf_exempt
def delete_review_coach(request, review_id):
    review = get_object_or_404(ReviewCoach, pk=review_id)

    if not review.can_delete(request.user):
        return JsonResponse({'status': 'error', 'message': 'Anda tidak memiliki izin untuk menghapus review ini'}, status=403)

    review.delete()
    return JsonResponse({'status': 'success', 'message': 'Review berhasil dihapus'})


def get_reviews_json(request, coach_id):
    coach = get_object_or_404(Coach, pk=coach_id)
    reviews = coach.reviews.all()

    reviews_data = []
    for review in reviews:
        can_edit = review.can_edit(request.user)
        can_delete = review.can_delete(request.user)

        reviews_data.append({
            'id': review.id,
            'reviewer_name': review.reviewer_name if review.reviewer_name else (
                review.user.username if review.user else "Anonim"
            ),
            'rating': float(review.rating),
            'review_text': review.review_text,
            'tanggal_dibuat': review.created_at.strftime('%Y-%m-%d %H:%M'),
            'user_id': review.user.id if review.user else None,
            'can_edit': can_edit,
            'can_delete': can_delete,
        })

    return JsonResponse(reviews_data, safe=False)


# ====== ENDPOINT KHUSUS AJAX BUAT FLUTTER ======
@csrf_exempt
def add_review_coach_ajax(request, coach_id):
    """Endpoint AJAX untuk tambah review coach (dipakai Flutter)."""
    if request.method != 'POST':
        return JsonResponse(
            {'status': 'error', 'message': 'Metode permintaan tidak valid.'},
            status=405
        )

    coach = get_object_or_404(Coach, pk=coach_id)

    form = ReviewCoachForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.coach = coach

        # sama kayak lapangan: kalau login, simpan user
        if request.user.is_authenticated:
            review.user = request.user
            if not review.reviewer_name:
                review.reviewer_name = request.user.username
        else:
            # anonymous → pakai "Anonim" kalau kosong
            if not review.reviewer_name:
                review.reviewer_name = "Anonim"

        review.save()

        return JsonResponse(
            {
                'status': 'success',
                'message': 'Review berhasil ditambahkan!',
                'review_id': review.id,
            },
            status=201,
        )

    errors = dict(form.errors.items())
    return JsonResponse(
        {'status': 'error', 'errors': errors},
        status=400,
    )

@csrf_exempt
@require_POST
def edit_review_coach_ajax(request, review_id):
    review = get_object_or_404(ReviewCoach, pk=review_id)

    if not review.can_edit(request.user):
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Anda tidak memiliki izin untuk mengedit review ini.'
            },
            status=403
        )

    form = ReviewCoachForm(request.POST, instance=review)
    if form.is_valid():
        form.save()
        return JsonResponse(
            {
                'status': 'success',
                'message': 'Review berhasil diupdate.',
                'review_id': review.id,
            },
            status=200
        )

    errors = dict(form.errors.items())
    return JsonResponse(
        {
            'status': 'error',
            'errors': errors,
        },
        status=400
    )
