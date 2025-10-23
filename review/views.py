from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.db.models import Q, Avg

from main.forms import ReviewForm
from main.models import Lapangan
from review.models import Review

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

#==========================================================
# Semua fungsi buat review hehe
#==========================================================

def show_review_lapangan(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)
        
    reviews = Review.objects.filter(lapangan=lapangan)
    review_form = ReviewForm()

    context = {
        'lapangan': lapangan,
        'reviews': reviews,
        'review_form': review_form,
        'is_authenticated': request.user.is_authenticated 
    }
    return render(request, 'review/lapangan/review_lapangan.html', context)

def show_feeds_review_lapangan(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)
        
    context = {
        'lapangan': lapangan,
    }
    return render(request, 'review/lapangan/feeds_review_lapangan.html', context)

def show_form_review_lapangan(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.lapangan = lapangan
            new_review.save()
            
            # PAKAI FUNGSI UPDATE YANG BARU, BUKAN Avg()!
            update_lapangan_rating(lapangan)
            
            return redirect('main:show_feeds_review_lapangan', lapangan_id=lapangan.id)

    else:
        form = ReviewForm()

    context = {
        'lapangan': lapangan,
        'review_form': form,
    }
    return render(request, 'review/lapangan/form_review_lapangan.html', context)

def get_single_review_json(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
        data = {
            'id': review.id,
            'reviewer_name': review.reviewer_name,
            'rating': float(review.rating),
            'review_text': review.review_text,
            'gambar': review.gambar,
        }
        return JsonResponse(data)
    except Review.DoesNotExist:
        return JsonResponse({'detail': 'Review not found'}, status=404)

def show_edit_review_lapangan(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
            
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                
                # PAKAI FUNGSI UPDATE YANG BARU!
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
            new_review.save()
            
            # Update rating lapangan
            update_lapangan_rating(lapangan)
            
            return JsonResponse({'status': 'success', 'message': 'Review berhasil ditambahkan!'}, status=201)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Metode permintaan tidak valid.'}, status=405)

#=====================================
def update_lapangan_rating(lapangan):
    """Update rating lapangan - Pakai original_rating"""
    new_reviews = Review.objects.filter(lapangan=lapangan)
    
    # Jika tidak ada review baru, reset ke original_rating
    if new_reviews.count() == 0:
        lapangan.rating = lapangan.original_rating
        lapangan.save()
        print(f"🔄 Reset to original rating: {lapangan.original_rating}")
        return lapangan.rating
    
    # Hitung dengan original_rating sebagai base
    total_rating = lapangan.original_rating
    total_reviews = 1
    
    for review in new_reviews:
        total_rating += float(review.rating)
        total_reviews += 1
    
    new_rating = round(total_rating / total_reviews, 1)
    lapangan.rating = new_rating
    lapangan.save()
    
    print(f"✅ FINAL: {total_rating} / {total_reviews} = {new_rating}")
    return new_rating

def get_reviews_json(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return JsonResponse({'detail': 'Lapangan not found'}, status=404)
        
    reviews_from_model = Review.objects.filter(lapangan=lapangan).order_by('-tanggal_dibuat')
    
    all_reviews = []
    total_reviews_count = reviews_from_model.count()
    
    # Hitung jumlah total review untuk ditampilkan
    dataset_has_review = bool(lapangan.review and lapangan.review.strip())
    if dataset_has_review:
        total_reviews_count += 1  # Tambah 1 untuk dataset CSV
    
    # 1. Tambahkan review dari dataset CSV (jika ada review text)
    if dataset_has_review:
        all_reviews.append({
            'id': 0,  # ID khusus untuk dataset
            'reviewer_name': 'Pengguna Lain',
            'rating': float(lapangan.rating),  # Rating asli dari CSV
            'review_text': lapangan.review,
            'tanggal_dibuat': 'Data Awal',
            'gambar': None,
            'can_edit': False,
            'can_delete': False,
            'is_dataset': True
        })
    
    # 2. Tambahkan review dari model Review (yang baru)
    for review in reviews_from_model:
        all_reviews.append({
            'id': review.id,
            'reviewer_name': review.reviewer_name,
            'rating': float(review.rating),
            'review_text': review.review_text,
            'tanggal_dibuat': review.tanggal_dibuat.strftime("%Y-%m-%d %H:%M"),
            'gambar': review.gambar,
            'can_edit': True,
            'can_delete': True,
            'is_dataset': False
        })
    
    return JsonResponse(all_reviews, safe=False)

@csrf_exempt
def update_review(request, review_id):
    if request.method == 'POST':
        try:
            review = Review.objects.get(pk=review_id)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                update_lapangan_rating(review.lapangan)
                return JsonResponse({'status': 'success', 'message': 'Review berhasil diupdate!'})
            else:
                errors = dict(form.errors.items())
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
                
        except Review.DoesNotExist:  # TAMBAH INI
            return JsonResponse({'status': 'error', 'message': 'Review tidak ditemukan.'}, status=404)

@csrf_exempt
@require_POST
def delete_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
        lapangan = review.lapangan
        review.delete()
        update_lapangan_rating(lapangan)
        return JsonResponse({'status': 'success', 'message': 'Review berhasil dihapus.'}, status=200)
    except Review.DoesNotExist:  # TAMBAH INI
        return JsonResponse({'status': 'error', 'message': 'Review tidak ditemukan.'}, status=404)