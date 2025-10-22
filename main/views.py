from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .models import UserProfile, Avatar, Event
from .forms import EventForm
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
def update_profile_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_avatar_id = data.get('avatar_id')
            new_sport_key = data.get('olahraga_favorit')

            profile = get_object_or_404(UserProfile, user=request.user)

            if new_avatar_id:
                try:
                    avatar = Avatar.objects.get(pk=new_avatar_id)
                    profile.avatar = avatar
                except Avatar.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Avatar tidak valid'}, status=400)
            
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

# <-- THIS IS THE REQUIRED VIEW FUNCTION
def get_events_json(request):
    event_objects = Event.objects.all().order_by('-tanggal')
    
    search_name = request.GET.get('search_name', '')
    search_location = request.GET.get('search_location', '')
    search_sport = request.GET.get('search_sport', '')

    if search_name:
        event_objects = event_objects.filter(nama__icontains=search_name)
    
    if search_location:
        event_objects = event_objects.filter(lokasi__icontains=search_location)        
    if search_sport:
        event_objects = event_objects.filter(olahraga=search_sport)
    
    event_list = []
    for event in event_objects:
        event_list.append({
            'id': event.id,
            'nama': event.nama,
            'olahraga': event.get_olahraga_display(), 
            'deskripsi': event.deskripsi,
            'tanggal': event.tanggal.strftime('%Y-%m-%d'),
            'lokasi': event.lokasi,
            'kontak': event.kontak,
            'biaya': event.biaya,
            'thumbnail': event.thumbnail,
            'jam': event.jam.strftime('%H:%M:%S') if event.jam else None, 
            'user_id': event.user.id
        })
        
    return JsonResponse({'events': event_list})

@login_required(login_url='/login/')
def get_event_detail_ajax(request, id):
    try:
        event = get_object_or_404(Event, pk=id)
        
        # Kirim data event sebagai JSON
        data = {
            'id': event.id,
            'nama': event.nama,
            'olahraga': event.olahraga, # Kirim value (e.g., 'sepakbola')
            'deskripsi': event.deskripsi,
            'tanggal': event.tanggal.strftime('%Y-%m-%d'),
            'lokasi': event.lokasi,
            'kontak': event.kontak,
            'biaya': event.biaya,
            'thumbnail': event.thumbnail,
            'jam': event.jam.strftime('%H:%M') if event.jam else '',
        }
        return JsonResponse({'status': 'success', 'data': data})
    
    except Event.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Event tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required(login_url='/login/') # 1. Tambahkan ini
@csrf_exempt
def add_event_ajax(request):  # <--- INI FUNGSINYA
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            # 2. Jangan langsung save
            event = form.save(commit=False) 
            
            # 3. Tambahkan user yang sedang login
            # (Ganti 'user' jika nama field di model Anda beda, misal 'author')
            event.user = request.user 
            
            # 4. Baru save ke database
            event.save() 
            
            return JsonResponse({"status": "success", "message": "Event berhasil ditambahkan!"}, status=201)
        else:
            # Kirim error validasi form ke frontend
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    
    return JsonResponse({"status": "error", "message": "Metode permintaan tidak valid."}, status=405)

@login_required(login_url='/login/')
@csrf_exempt
@require_POST
def edit_event_ajax(request, id):
    try:
        event = get_object_or_404(Event, pk=id)
        
        # Pastikan hanya pembuat event yang bisa meng-edit
        if event.user != request.user:
            return HttpResponseForbidden(JsonResponse({'status': 'error', 'message': 'Anda tidak punya izin untuk meng-edit event ini.'}))
        
        # Muat form dengan data dari POST dan instance event yang ada
        form = EventForm(request.POST, instance=event)
        
        if form.is_valid():
            form.save() # Simpan perubahan
            return JsonResponse({"status": "success", "message": "Event berhasil diperbarui!"}, status=200)
        else:
            # Kirim error validasi form ke frontend
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    except Event.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Event tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def show_event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'event_detail.html', {'event': event})

@login_required(login_url='/login/')
def show_event(request):
    context = {
        'app_name' : 'ASKMO',
        'username': request.user.username,
        'last_login': request.COOKIES.get('last_login', 'Tidak Pernah'),
    }
    return render(request, "event.html", context)

@login_required(login_url='/login/')
@require_POST  
@csrf_exempt
def delete_event_ajax(request, id):
    try:
        event = get_object_or_404(Event, pk=id)
        
        if event.user != request.user:
            return HttpResponseForbidden(JsonResponse({'status': 'error', 'message': 'Anda tidak punya izin untuk menghapus event ini.'}))
        
        event.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Event berhasil dihapus.'})

    except Event.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Event tidak ditemukan.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)