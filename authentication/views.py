from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return JsonResponse({
            'username': user.username,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'status': True,
            'message': 'Login successful!'
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, account is disabled."
            }, status=401)

    else:
        return JsonResponse({
            "status": False,
            "message": "Login failed, please check your username or password."
        }, status=401)
    
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']

        # check kalopassword cocok
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        # check kalo username sudah dipake
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        # check kalo password mirip sama username
        if username.lower() in password1.lower() or password1.lower() in username.lower():
            return JsonResponse({
                "status": False,
                "message": "Password cannot be similar to username."
            }, status=400)
        
        # check panjang password (minimal 8 karakter)
        if len(password1) < 8:
            return JsonResponse({
                "status": False,
                "message": "Password must be at least 8 characters long."
            }, status=400)
        
        # check kalo password mengandung minimal satu huruf kapital
        if not any(char.isupper() for char in password1):
            return JsonResponse({
                "status": False,
                "message": "Password must contain at least one uppercase letter."
            }, status=400)
        
        # check kalo password mengandung minimal satu angka
        if not any(char.isdigit() for char in password1):
            return JsonResponse({
                "status": False,
                "message": "Password must contain at least one number."
            }, status=400)
        
        # create user baru
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

@csrf_exempt
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)