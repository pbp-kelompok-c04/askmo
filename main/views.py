from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers

from main import models
from main.forms import LapanganForm, CoachForm, EventForm, ReviewForm
from main.models import Lapangan, Coach, Event, Review
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

from django.db.models import Q, Avg

def show_main(request):
    context = {
        'app_name' : 'ASKMO',
        'username': request.user.username,
        'last_login': request.COOKIES.get('last_login', 'Tidak Pernah'),
    }
    return render(request, "main.html", context)

@csrf_exempt
def register_ajax(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Akun berhasil dibuat!'}, status=201)
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    return JsonResponse({"status": "error", "message": "Metode permintaan tidak valid."}, status=405)

@csrf_exempt
def login_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = JsonResponse({'status': 'success', 'message': 'Login berhasil!'})
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            return JsonResponse({'status': 'error', 'message': 'Username atau password salah.'}, status=401)
    return JsonResponse({"status": "error", "message": "Metode permintaan tidak valid."}, status=405)

@csrf_exempt
def logout_ajax(request):
    if request.method == 'POST':
        logout(request)
        response = JsonResponse({"status": "success", "message": "Anda sudah logout."})
        response.delete_cookie('last_login')
        return response
    return JsonResponse({"status": "error", "message": "Metode permintaan tidak valid."}, status=405)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun Anda berhasil dibuat!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response

    else:
        form = AuthenticationForm(request)
    context = {'form': form}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

@csrf_exempt
@require_POST
@login_required
def add_lapangan_ajax(request):
    nama = strip_tags(request.POST.get("nama"))
    deskripsi = strip_tags(request.POST.get("deskripsi"))
    olahraga = request.POST.get("olahraga")
    thumbnail = request.POST.get("thumbnail")
    rating = float(request.POST.get("rating",0.0))
    refund = request.POST.get("refund") == "on"
    tarif_per_sesi = request.POST.get("tarif_per_sesi")
    kontak = strip_tags(request.POST.get("kontak"))
    alamat = strip_tags(request.POST.get("alamat"))
    review = strip_tags(request.POST.get("review", "")) or None
    peraturan = strip_tags(request.POST.get("peraturan", "")) or None
    fasilitas = strip_tags(request.POST.get("fasilitas", "")) or None

    new_lapangan = Lapangan(
        id=uuid.uuid4(),
        nama=nama,
        deskripsi=deskripsi,
        olahraga=olahraga,
        thumbnail=thumbnail,
        rating=rating,
        refund=refund,
        tarif_per_sesi=tarif_per_sesi,
        kontak=kontak,
        alamat=alamat,
        review=review,
        peraturan=peraturan,
        fasilitas=fasilitas
    )

    new_lapangan.save()

    return HttpResponse(b"CREATED", status=201)

def show_xml(request):
    lapangan_list = Lapangan.objects.all()
    xml_data = serializers.serialize("xml", lapangan_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    lapangan_list = Lapangan.objects.all()
    data = [
        {
            'id': str(lapangan.id),
            'nama': lapangan.nama,
            'deskripsi': lapangan.deskripsi,
            'olahraga': lapangan.olahraga,
            'thumbnail': lapangan.thumbnail,
            'rating': lapangan.rating,
            'refund': lapangan.refund,
            'tarif_per_sesi': str(lapangan.tarif_per_sesi),
            'kontak': lapangan.kontak,
            'alamat': lapangan.alamat,
            'review': lapangan.review,
            'peraturan': lapangan.peraturan,
            'fasilitas': lapangan.fasilitas,
        }
        for lapangan in lapangan_list
    ]
    return JsonResponse(data, safe=False)

def show_xml_by_id(request, lapangan_id):
    try:
        lapangan_item = Lapangan.objects.filter(pk=lapangan_id)
        xml_data = serializers.serialize("xml", lapangan_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Lapangan.DoesNotExist:
        return HttpResponse(status=404)

# In main/views.py

def show_json_by_id(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
        data = {
            'id': str(lapangan.id),
            'nama': lapangan.nama,
            'deskripsi': lapangan.deskripsi,
            'olahraga': lapangan.get_olahraga_display(), 
            'thumbnail': lapangan.thumbnail,
            'rating': lapangan.rating,
            'refund': lapangan.refund,
            'tarif_per_sesi': str(lapangan.tarif_per_sesi),
            'kontak': lapangan.kontak,
            'alamat': lapangan.alamat,
            'kecamatan': lapangan.kecamatan, 
            'review': lapangan.review,
            'peraturan': lapangan.peraturan,
            'fasilitas': lapangan.fasilitas,
        }
        return JsonResponse(data)
    except Lapangan.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)

def show_lapangan_by_alamat_xml(request, alamat):
    lapangan_list = Lapangan.objects.filter(alamat__icontains=alamat)
    xml_data = serializers.serialize("xml", lapangan_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_lapangan_by_alamat_json(request, alamat):
    lapangan_list = Lapangan.objects.filter(alamat__icontains=alamat)
    data = [
        {
            'id': str(lapangan.id),
            'nama': lapangan.nama,
            'deskripsi': lapangan.deskripsi,
            'olahraga': lapangan.olahraga,
            'thumbnail': lapangan.thumbnail,
            'rating': lapangan.rating,
            'refund': lapangan.refund,
            'tarif_per_sesi': str(lapangan.tarif_per_sesi),
            'kontak': lapangan.kontak,
            'alamat': lapangan.alamat,
            'review': lapangan.review,
            'peraturan': lapangan.peraturan,
            'fasilitas': lapangan.fasilitas,
        }
        for lapangan in lapangan_list
    ]
    return JsonResponse(data, safe=False)

#ini buat filter by kecamatannya
def show_lapangan_by_kecamatan_xml(request, kecamatan):
    lapangan_list = Lapangan.objects.filter(kecamatan__iexact=kecamatan)
    xml_data = serializers.serialize("xml", lapangan_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_lapangan_by_kecamatan_json(request, kecamatan):
    lapangan_list = Lapangan.objects.filter(kecamatan__iexact=kecamatan)
    data = [
        {
            'id': str(lapangan.id),
            'nama': lapangan.nama,
            'deskripsi': lapangan.deskripsi,
            'olahraga': lapangan.olahraga,
            'thumbnail': lapangan.thumbnail,
            'rating': lapangan.rating,
            'refund': lapangan.refund,
            'tarif_per_sesi': str(lapangan.tarif_per_sesi),
            'kontak': lapangan.kontak,
            'alamat': lapangan.alamat,
            'kecamatan': lapangan.kecamatan,
            'review': lapangan.review,
            'peraturan': lapangan.peraturan,
            'fasilitas': lapangan.fasilitas,
        }
        for lapangan in lapangan_list
    ]
    return JsonResponse(data, safe=False)

@login_required
def show_lapangan_dashboard(request):
    search_nama = request.GET.get('nama', '')
    search_kecamatan = request.GET.get('kecamatan', '')
    search_olahraga = request.GET.get('olahraga', '')

    lapangan_list = Lapangan.objects.all()

    if search_nama :
        lapangan_list = lapangan_list.filter(nama__icontains=search_nama)
    if search_kecamatan :
        lapangan_list = lapangan_list.filter(kecamatan__icontains=search_kecamatan)
    if search_olahraga :
        lapangan_list = lapangan_list.filter(olahraga__icontains=search_olahraga)

    context = {
        'lapangan_list' : lapangan_list,
        'search_values' : request.GET,
        'olahraga_choices' : Lapangan.OLAHRAGA_CHOICES,
    }
    return render(request, 'lapangan/dashboard_lapangan.html', context)

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
    return render(request, 'lapangan/review_lapangan.html', context)

def show_feeds_review_lapangan(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return HttpResponse("Lapangan tidak ditemukan.", status=404)
        
    context = {
        'lapangan': lapangan,
    }
    return render(request, 'lapangan/feeds_review_lapangan.html', context)

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
            
            average_rating = Review.objects.filter(lapangan=lapangan).aggregate(Avg('rating'))['rating__avg'] or 0.0
            lapangan.rating = round(average_rating, 1)
            lapangan.save()
            
            return redirect('main:show_feeds_review_lapangan', lapangan_id=lapangan.id)

    else:
        form = ReviewForm()

    context = {
        'lapangan': lapangan,
        'review_form': form,
    }
    return render(request, 'lapangan/form_review_lapangan.html', context)


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
            
            average_rating = Review.objects.filter(lapangan=lapangan).aggregate(Avg('rating'))['rating__avg'] or 0.0
            lapangan.rating = round(average_rating, 1)
            lapangan.save()

            return JsonResponse({'status': 'success', 'message': 'Review berhasil ditambahkan!'}, status=201)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Metode permintaan tidak valid.'}, status=405)

    
@csrf_exempt
def update_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
        if review.session_key != request.session.session_key:
            return JsonResponse({'status': 'error', 'message': 'Anda tidak memiliki izin untuk mengedit review ini.'}, status=403)
            
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                
                lapangan = review.lapangan
                average_rating = Review.objects.filter(lapangan=lapangan).aggregate(Avg('rating'))['rating__avg'] or 0.0
                lapangan.rating = round(average_rating, 1)
                lapangan.save()
                
                return JsonResponse({'status': 'success', 'message': 'Review berhasil diupdate!'})
            else:
                errors = dict(form.errors.items())
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
                
    except Review.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Review tidak ditemukan.'}, status=404)

@csrf_exempt
@require_POST
def delete_review(request, review_id):
    try:
        review = Review.objects.get(pk=review_id)
        lapangan = review.lapangan
        
        review.delete()
        
        average_rating = Review.objects.filter(lapangan=lapangan).aggregate(Avg('rating'))['rating__avg'] or 0.0
        lapangan.rating = round(average_rating, 1)
        lapangan.save()
        
        return JsonResponse({'status': 'success', 'message': 'Review berhasil dihapus.'}, status=200)
    except Review.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Review tidak ditemukan.'}, status=404)
    

def get_reviews_json(request, lapangan_id):
    try:
        lapangan = Lapangan.objects.get(pk=lapangan_id)
    except Lapangan.DoesNotExist:
        return JsonResponse({'detail': 'Lapangan not found'}, status=404)
        
    reviews = Review.objects.filter(lapangan=lapangan).order_by('-tanggal_dibuat')
    
    # Untuk sementara, set semua bisa edit/hapus (nanti ganti dengan session logic)
    current_session = request.session.session_key
    can_delete_review = True  # Ganti dengan logic session nanti

    data = [
        {
            'id': review.id,
            'reviewer_name': review.reviewer_name,
            'rating': float(review.rating),
            'review_text': review.review_text,
            'tanggal_dibuat': review.tanggal_dibuat.strftime("%Y-%m-%d %H:%M"),
            'gambar': review.gambar,
            'can_edit': True, 
            'can_delete': True  
        }
        for review in reviews
    ]
    return JsonResponse(data, safe=False)

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
                
                lapangan = review.lapangan
                average_rating = Review.objects.filter(lapangan=lapangan).aggregate(Avg('rating'))['rating__avg'] or 0.0
                lapangan.rating = round(average_rating, 1)
                lapangan.save()
                
                return redirect('main:show_feeds_review_lapangan', lapangan_id=review.lapangan.id)
        else:
            form = ReviewForm(instance=review)

        context = {
            'review': review,
            'review_form': form,
        }
        return render(request, 'lapangan/edit_review_lapangan.html', context)
        
    except Review.DoesNotExist:
        return HttpResponse("Review tidak ditemukan.", status=404)