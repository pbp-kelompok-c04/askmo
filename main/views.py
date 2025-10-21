from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .models import UserProfile, Avatar
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout

import datetime
import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
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

