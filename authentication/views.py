from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return JsonResponse({
                'user_id': user.id,
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

        # check jika password cocok
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        # check jika username sudah dipakai (sudah tidak tersedia)
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        # check jika password mirip sama username
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
        
        # check password mengandung minimal satu angka
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

# --- Google OAuth: create-or-login ---

GOOGLE_WEB_CLIENT_ID = "990231107870-uheikav6hi1qovpmgfbspecru0h4hbou.apps.googleusercontent.com"

ALLOWED_AUDIENCES = {
    GOOGLE_WEB_CLIENT_ID,
    "990231107870-jfeuksfhs309v6k217pqo87a379logcp.apps.googleusercontent.com"
}

def _name_to_first_last(full_name: str):
    full_name = (full_name or "").strip()
    if not full_name:
        return ("", "")
    parts = full_name.split()
    first = parts[0]
    last = " ".join(parts[1:]) if len(parts) > 1 else ""
    return (first[:150], last[:150])

@csrf_exempt
def google_login(request):
    if request.method != "POST":
        return JsonResponse({"status": False, "message": "Invalid request method."}, status=400)

    data = {}
    try:
        if request.body:
            data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = {}

    if not data:
        data = request.POST

    id_token_str = data.get("id_token")
    access_token = data.get("access_token")

    if not id_token_str and not access_token:
        return JsonResponse({"status": False, "message": "Token Google tidak ditemukan"}, status=400)

    try:
        email = None
        full_name = None

        if id_token_str:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=None,
            )

            aud = idinfo.get("aud")
            if aud not in ALLOWED_AUDIENCES:
                return JsonResponse(
                    {"status": False, "message": f"Invalid token audience (aud): {aud}"},
                    status=400,
                )

            email = idinfo.get("email")
            full_name = idinfo.get("name")

        else:
            # Access token path
            userinfo_resp = requests.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=8,
            )
            if userinfo_resp.status_code != 200:
                return JsonResponse({"status": False, "message": "Gagal mengambil data user dari Google"}, status=400)

            userinfo = userinfo_resp.json()
            email = userinfo.get("email")
            full_name = userinfo.get("name")

        if not email:
            return JsonResponse({"status": False, "message": "Tidak bisa mendapatkan email dari akun Google"}, status=400)

        user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()

        created = False
        if user is None:
            first, last = _name_to_first_last(full_name or "")
            user = User(username=email, email=email, first_name=first, last_name=last)
            user.set_unusable_password()
            user.save()
            created = True

        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return JsonResponse({
            "user_id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "created": created,
            "status": True,
            "message": "Login successful!"
        }, status=200)

    except Exception as e:
        return JsonResponse({"status": False, "message": str(e)}, status=400)

