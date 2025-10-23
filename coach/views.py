from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .models import Coach, CoachWishlist
from main.models import Collection
from .forms import CoachForm
from django.db import models

User = get_user_model()

# ==============================================================================
# VIEW UNTUK HALAMAN PUBLIK
# ==============================================================================

def coach_list_view(request):
    coaches_list = Coach.objects.all().order_by('name')

    # Ambil nilai dari parameter GET di URL untuk filter
    search_name = request.GET.get('name', '')
    search_location = request.GET.get('location', '')
    search_sport = request.GET.get('sport_branch', '')

    # Lakukan filter pada daftar jika ada parameter pencarian yang diisi
    if search_name:
        coaches_list = coaches_list.filter(name__icontains=search_name)
    
    if search_location:
        coaches_list = coaches_list.filter(location__icontains=search_location)

    if search_sport:
        coaches_list = coaches_list.filter(sport_branch__icontains=search_sport)

    # Kirim data 'coaches' yang sudah difilter (atau semua data jika tidak ada filter) ke template
    context = {
        'coaches': coaches_list,
        'search_values': request.GET  # Untuk mengisi kembali value di form pencarian
    }
    
    return render(request, 'coach/index.html', context)


def coach_detail_view(request, pk):
    coach_instance = get_object_or_404(Coach, pk=pk)
    
    is_saved_to_wishlist = CoachWishlist.objects.filter(
        coach=coach_instance, 
        user=request.user
    ).exists()

    contact_str = coach_instance.contact
    phone_number_cleaned = None
    whatsapp_number = None

    if '@' in contact_str:
        is_email = True
    else:
        phone_number_cleaned = ''.join(c for c in contact_str if c.isdigit() or c == '+')
        
        if phone_number_cleaned.startswith('0'):
            whatsapp_number = '62' + phone_number_cleaned[1:]
        elif phone_number_cleaned.startswith('+'):
            whatsapp_number = phone_number_cleaned[1:]
        elif phone_number_cleaned.startswith('62'):
            whatsapp_number = phone_number_cleaned
        else:
            whatsapp_number = phone_number_cleaned

    context = {
        'coach': coach_instance,
        'phone_number_cleaned': phone_number_cleaned,
        'whatsapp_number': whatsapp_number,
        'is_saved_to_wishlist': is_saved_to_wishlist
    }
    return render(request, 'coach/coach_detail.html', context)


# ==============================================================================
# VIEW UNTUK OTENTIKASI ADMIN KUSTOM
# ==============================================================================

def login_view(request):
    """
    Menangani proses login untuk admin (pengguna dengan status 'is_staff').
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('coach:dashboard') # Jika sudah login sebagai staff, langsung ke dashboard

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            # Verifikasi bahwa user ada dan merupakan seorang staff
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('coach:dashboard')
            else:
                form.add_error(None, "Invalid credentials or you do not have admin access.")
    else:
        form = AuthenticationForm()
    return render(request, 'coach_admin/login.html', {'form': form})


def logout_view(request):
    """
    Menangani proses logout untuk admin.
    """
    logout(request)
    return redirect('coach:login') # Redirect ke halaman login setelah logout


# ==============================================================================
# DECORATOR UNTUK KEAMANAN PANEL ADMIN
# ==============================================================================

def staff_required(view_func):
    """
    Decorator yang memastikan hanya pengguna yang login dan berstatus 'staff'
    yang dapat mengakses view yang dilindunginya.
    """
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated_view_func


# ==============================================================================
# VIEW UNTUK PANEL ADMIN KUSTOM (CRUD)
# ==============================================================================

@staff_required
def dashboard_view(request):
    """
    Menampilkan halaman utama panel admin dengan daftar semua coach. (Read)
    """
    coaches = Coach.objects.all().order_by('name')
    return render(request, 'coach_admin/dashboard.html', {'coaches': coaches})


@staff_required
def coach_create_view(request):
    """
    Menangani pembuatan data coach baru. (Create)
    """
    if request.method == 'POST':
        form = CoachForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('coach:dashboard')
    else:
        form = CoachForm()
    return render(request, 'coach_admin/coach_form.html', {'form': form, 'title': 'Add New Coach'})


@staff_required
def coach_update_view(request, pk):
    """
    Menangani pembaruan data coach yang sudah ada berdasarkan Primary Key (pk). (Update)
    """
    coach = get_object_or_404(Coach, pk=pk)
    if request.method == 'POST':
        form = CoachForm(request.POST, request.FILES, instance=coach)
        if form.is_valid():
            form.save()
            return redirect('coach:dashboard')
    else:
        form = CoachForm(instance=coach)
    return render(request, 'coach_admin/coach_form.html', {'form': form, 'title': f'Edit {coach.name}'})


@staff_required
def coach_delete_view(request, pk):
    """
    Menangani penghapusan data coach. (Delete)
    """
    coach = get_object_or_404(Coach, pk=pk)
    if request.method == 'POST':
        coach.delete()
        return redirect('coach:dashboard')
    return render(request, 'coach_admin/coach_confirm_delete.html', {'coach': coach})

@login_required
def add_to_wishlist_view(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    user = request.user
    
    wishlist_item = CoachWishlist.objects.filter(user=user, coach=coach)
    
    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        CoachWishlist.objects.create(user=user, coach=coach)        
    return redirect('coach:coach_detail', pk=pk)

@login_required
def coach_wishlist_list_view(request):
    wishlist_items = CoachWishlist.objects.filter(user=request.user)
    coaches_in_wishlist = [item.coach for item in wishlist_items]
    context = {
        'coaches': coaches_in_wishlist
    }
    return render(request, 'wishlist_coach_list.html', context)

@login_required
def coach_wishlist_list_view(request):
    wishlist_items = CoachWishlist.objects.filter(user=request.user)
    coaches_in_wishlist = [item.coach for item in wishlist_items]
    context = {
        'coach_list': coaches_in_wishlist
    }
    return render(request, 'wishlist/wishlist_coach_list.html', context)