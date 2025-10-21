from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers

from main.forms import LapanganForm, CoachForm, EventForm
from main.models import Lapangan, Coach, Event, Collection
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

    if request.user.is_authenticated:
        for lapangan in lapangan_list:
            lapangan.is_saved_to_wishlist = Collection.objects.filter(
                user=request.user,
                lapangan=lapangan
            ).exists()

    context = {
        'lapangan_list' : lapangan_list,
        'search_values' : request.GET,
        'olahraga_choices' : Lapangan.OLAHRAGA_CHOICES,
    }
    return render(request, 'lapangan/dashboard_lapangan.html', context)


