import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from .models import UserProfile, Avatar
from main.models import Collection
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers

from main.forms import LapanganForm, CoachForm, EventForm
from main.models import Lapangan, Coach, Event
from django.db.models import Q

from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .models import UserProfile, Avatar
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout

import datetime
import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags;
from .models import UserProfile, Avatar 

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

@login_required(login_url='/login/')
def show_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    avatars = Avatar.objects.all()
    olahraga_choices = UserProfile.OLAHRAGA_CHOICES 

    context = {
        'profile': profile,
        'avatars': avatars,
        'olahraga_choices': olahraga_choices,
        'current_sport_key': profile.olahraga_favorit,
    }
    return render(request, 'profile.html', context) 

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def show_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    avatars = Avatar.objects.all()
    olahraga_choices = UserProfile.OLAHRAGA_CHOICES 

    context = {
        'profile': profile,
        'avatars': avatars,
        'olahraga_choices': olahraga_choices,
        'current_sport_key': profile.olahraga_favorit,
    }
    return render(request, 'profile.html', context) 

@login_required(login_url='/login/')
@csrf_exempt
def update_profile_ajax(request):
    if request.method == 'POST':
        # *Logika update akan diisi di langkah implementasi Edit Profile*
        try:
            data = json.loads(request.body)
            new_avatar_id = data.get('avatar_id')
            new_sport_key = data.get('olahraga_favorit')

            profile = get_object_or_404(UserProfile, user=request.user)

            # Update Avatar
            if new_avatar_id:
                try:
                    avatar = Avatar.objects.get(pk=new_avatar_id)
                    profile.avatar = avatar
                except Avatar.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Avatar tidak valid'}, status=400)
            
            # Update Olahraga Favorit
            if new_sport_key:
                valid_sports = [key for key, _ in UserProfile.OLAHRAGA_CHOICES]
                if new_sport_key in valid_sports:
                    profile.olahraga_favorit = new_sport_key
                else:
                    return JsonResponse({'status': 'error', 'message': 'Pilihan olahraga tidak valid'}, status=400)

            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Profil berhasil diperbarui'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return HttpResponseForbidden()

@login_required
@require_POST
def create_collection_ajax(request):
    try:
        data = json.loads(request.body)
        collection_name = data.get('name', '').strip()
        
        if not collection_name:
            return JsonResponse({'status': 'error', 'message': 'Nama koleksi tidak boleh kosong.'}, status=400)
        
        if Collection.objects.filter(user=request.user, name=collection_name).exists():
            return JsonResponse({'status': 'error', 'message': f'Koleksi bernama "{collection_name}" sudah ada.'}, status=400)

        # Buat objek Collection baru (tanpa is_public/is_shared)
        new_collection = Collection.objects.create(
            user=request.user,
            name=collection_name,
            # is_public dan is_shared tidak dimasukkan
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Koleksi "{collection_name}" berhasil dibuat!',
            'collection_id': new_collection.id,
            'collection_name': new_collection.name
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Gagal membuat koleksi: {str(e)}'}, status=500)
    return HttpResponseForbidden()

@login_required
def get_user_collections_for_item_ajax(request, item_type, item_id):
    collections = Collection.objects.filter(user=request.user).order_by('-created_at')
    collections_data = []

    if item_type == 'lapangan':
        ItemModel = Lapangan
    elif item_type == 'coach':
        ItemModel = Coach
    else:
        return JsonResponse({'status': 'error', 'message': 'Tipe item tidak valid'}, status=400)
    
    try:
        item = get_object_or_404(ItemModel, pk=item_id)
    except ItemModel.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item tidak ditemukan'}, status=404)

    for collection in collections:
        if item_type == 'lapangan':
            is_saved = collection.lapangan.filter(pk=item_id).exists() # Menggunakan ManyToManyField 'lapangan'
        elif item_type == 'coach':
            is_saved = collection.coach.filter(pk=item_id).exists() # <--- TAMBAH INI (Menggunakan ManyToManyField 'coach')

        collections_data.append({
            'id': collection.id,
            'name': collection.name,
            'is_saved': is_saved,
        })

    return JsonResponse({'status': 'success', 'collections': collections_data})

@login_required
@require_POST
@csrf_exempt
def toggle_save_item_to_collection_ajax(request):
    try:
        data = json.loads(request.body)
        collection_id = data.get('collection_id')
        item_id = data.get('item_id')
        item_type = data.get('item_type')
        
        collection = get_object_or_404(Collection, pk=collection_id, user=request.user)

        if item_type == 'lapangan':
            ItemModel = Lapangan
            related_manager = collection.lapangan
        elif item_type == 'coach': 
            ItemModel = Coach
            related_manager = collection.coach
        else:
            return JsonResponse({'status': 'error', 'message': 'Tipe item tidak valid.'}, status=400)

        item = get_object_or_404(ItemModel, pk=item_id)

        if related_manager.filter(pk=item_id).exists():
            related_manager.remove(item)
            action = 'removed'
            message = f'Berhasil dihapus dari koleksi "{collection.name}"'
        else:
            related_manager.add(item)
            action = 'added'
            message = f'Berhasil ditambahkan ke koleksi "{collection.name}"'
        
        return JsonResponse({
            'status': 'success', 
            'action': action,
            'message': message,
            'collection_name': collection.name
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Gagal memproses permintaan: {str(e)}'}, status=500)
    
@login_required
def show_collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
    lapangan_list = collection.lapangan.all()
    coach_list = collection.coach.all()

    context = {
        'collection': collection,
        'lapangan_list': lapangan_list, 
        'coach_list': coach_list, 
    }
    return render(request, 'wishlist/collection_detail.html', context)

@login_required
@require_POST
@csrf_exempt
def edit_collection_name_ajax(request):
    try:
        data = json.loads(request.body)
        collection_id = data.get('collection_id')
        new_name = data.get('new_name', '').strip()

        if not new_name:
            return JsonResponse({'status': 'error', 'message': 'Nama koleksi tidak boleh kosong.'}, status=400)
        
        collection = get_object_or_404(Collection, pk=collection_id, user=request.user)
        
        if Collection.objects.filter(user=request.user, name=new_name).exclude(pk=collection_id).exists():
            return JsonResponse({'status': 'error', 'message': f'Koleksi bernama "{new_name}" sudah ada.'}, status=400)

        old_name = collection.name
        collection.name = new_name
        collection.save()

        return JsonResponse({
            'status': 'success', 
            'message': f'Nama koleksi berhasil diubah dari "{old_name}" menjadi "{new_name}".',
            'collection_name': new_name
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Gagal mengedit koleksi: {str(e)}'}, status=500)
    
@login_required
def add_to_coach_list(request, coach_id):
    return redirect(reverse('main:show_user_collections'))

@login_required
def show_wishlist_lapangan(request):
    user_collections = Collection.objects.filter(user=request.user)
    
    lapangan_list = Lapangan.objects.filter(collection__in=user_collections).distinct()
    
    context = {
        'lapangan_list': lapangan_list,
    }
    return render(request, 'wishlist/wishlist_lapangan_list.html', context)

@login_required
def show_wishlist_coach(request):
    user_collections = Collection.objects.filter(user=request.user)
    
    coach_list = Coach.objects.filter(collection__in=user_collections).distinct()
    
    context = {
        'coach_list': coach_list,
    }
    return render(request, 'wishlist/wishlist_coach_list.html', context)