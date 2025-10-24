# main/forms.py
from django.forms import ModelForm
from django import forms
from main.models import Lapangan, Coach, Event, UserProfile, Avatar # Pastikan semua model diimport
from review.models import Review, ReviewCoach # Import review models jika belum
from django.contrib.auth.forms import UserCreationForm # Import form registrasi default
from django.contrib.auth.models import User

# --- Form untuk Lapangan Admin Panel ---
class LapanganForm(forms.ModelForm):
    class Meta:
        model = Lapangan
        # Kecualikan field yang biasanya tidak diedit manual oleh admin
        exclude = ['id', 'rating', 'original_rating'] 
        widgets = {
            # Terapkan styling dasar atau class CSS framework kamu
            'nama': forms.TextInput(attrs={'placeholder': 'Nama Lapangan Olahraga'}),
            'deskripsi': forms.Textarea(attrs={'placeholder': 'Deskripsi singkat tentang lapangan...', 'rows': 4}),
            'olahraga': forms.Select(), # Gunakan Select widget default
            'thumbnail': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg'}),
            'refund': forms.CheckboxInput(), # Gunakan Checkbox default
            'tarif_per_sesi': forms.NumberInput(attrs={'placeholder': 'Contoh: 150000.00', 'step': '1000'}),
            'alamat': forms.Textarea(attrs={'placeholder': 'Alamat lengkap lapangan...', 'rows': 3}),
            'kecamatan': forms.TextInput(attrs={'placeholder': 'Kecamatan lokasi lapangan'}),
            'kontak': forms.TextInput(attrs={'placeholder': 'Nomor telepon (contoh: 08123456789)'}),
            'review': forms.Textarea(attrs={'placeholder': '(Opsional) Review awal atau catatan admin...', 'rows': 3}), 
            'peraturan': forms.Textarea(attrs={'placeholder': 'Peraturan penggunaan lapangan...', 'rows': 3}),
            'fasilitas': forms.Textarea(attrs={'placeholder': 'Fasilitas yang tersedia (toilet, parkir, dll.)...', 'rows': 3}),
        }
        labels = {
            'nama': 'Nama Lapangan',
            'deskripsi': 'Deskripsi',
            'olahraga': 'Cabang Olahraga',
            'thumbnail': 'URL Gambar Thumbnail',
            'refund': 'Bisa Refund?',
            'tarif_per_sesi': 'Tarif per Sesi (Rp)',
            'alamat': 'Alamat Lengkap',
            'kecamatan': 'Kecamatan',
            'kontak': 'Nomor Kontak Pengelola',
            'review': 'Review/Catatan Admin (Opsional)',
            'peraturan': 'Peraturan Lapangan',
            'fasilitas': 'Fasilitas',
        }
        help_texts = {
            'thumbnail': 'Masukkan URL gambar yang valid (diawali http:// atau https://)',
            'kontak': 'Masukkan nomor telepon yang dapat dihubungi.',
            'tarif_per_sesi': 'Masukkan angka saja, contoh: 150000',
        }

    # Validasi custom (opsional)
    def clean_kontak(self):
        kontak = self.cleaned_data.get('kontak')
        # Hapus spasi dan periksa apakah hanya angka (dan mungkin '+' di awal)
        if kontak:
            cleaned_kontak = ''.join(filter(str.isdigit, kontak.lstrip('+')))
            if not cleaned_kontak:
                raise forms.ValidationError("Nomor kontak tidak valid.")
            # Kamu bisa tambahkan validasi panjang nomor jika perlu
        return kontak
        
    def clean_rating(self):
        # Meskipun rating di-exclude, jika field ini ada di form lain, validasi ini bisa berguna
        rating = self.cleaned_data.get("rating", 0.0)
        if rating is not None and not (0.0 <= rating <= 5.0):
            raise forms.ValidationError("Rating harus antara 0.0 sampai 5.0")
        return rating

# --- Form lain yang sudah ada ---
class CoachForm(ModelForm): # Form ini mungkin sebenarnya ada di app 'coach'? Jika ya, biarkan di sana.
    class Meta:
        model = Coach
        fields = ["nama", "olahraga", "deskripsi", "kontak", "tarif_per_jam", "thumbnail"]

class EventForm(ModelForm):
    class Meta:
        model = Event
        # Kecualikan user karena akan diisi otomatis di view
        fields = ["nama", "deskripsi", "olahraga", "tanggal", "lokasi", "kontak", "thumbnail", "jam", "biaya"] 
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'jam': forms.TimeInput(attrs={'type': 'time'}),
            'deskripsi': forms.Textarea(attrs={'rows': 3}),
            # Tambahkan widget lain jika perlu
        }

class ReviewForm(ModelForm):
    rating = forms.DecimalField(
        label="Rating (0.0 - 5.0)",
        min_value=0.0,
        max_value=5.0,
        decimal_places=1,
        widget=forms.NumberInput(attrs={'step': '0.1', 'min': '0.0', 'max': '5.0'})
    )
    reviewer_name = forms.CharField(
        max_length=255,
        label="Nama",
        widget=forms.TextInput(attrs={'placeholder': 'Masukkan Nama Anda'})
    )
    class Meta:
        model = Review
        fields = ["reviewer_name", "rating", "review_text", "gambar"]
        widgets = {
            'review_text': forms.Textarea(attrs={'placeholder': 'Masukkan review Anda'}),
            'gambar': forms.URLInput(attrs={'placeholder': 'Masukkan URL gambar (opsional)'}),
        }
        labels = {
            'review_text': 'Masukan dan Saran Anda',
            'gambar': 'Gambar (URL)',
        }

class ReviewCoachForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', # Gunakan class CSS jika ada framework
            'placeholder': '1-5',
            'min': '1',
            'max': '5'
        })
    )
    class Meta:
        model = ReviewCoach
        fields = ['reviewer_name', 'rating', 'review_text']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'placeholder': 'Masukkan nama Anda'}),
            'review_text': forms.Textarea(attrs={'placeholder': 'Bagikan pengalaman Anda...', 'rows': 4}),
        }
        labels = {
            'reviewer_name': 'Nama Anda',
            'rating': 'Rating (1-5)',
            'review_text': 'Review',
        }

# --- Form Registrasi & Profil ---
class NewUserForm(UserCreationForm): # Inherit dari UserCreationForm
	class Meta:
		model = User # Gunakan model User bawaan Django
		fields = ("username", "email", "first_name", "last_name") # Tambahkan field yang diinginkan

	# Tambahkan validasi atau kustomisasi lain jika perlu

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['olahraga_favorit'] # Hanya field yang bisa diubah user
        labels = {
            'olahraga_favorit': 'Olahraga Favorit',
        }

class AvatarForm(forms.Form): # Form untuk memilih avatar
    avatar = forms.ModelChoiceField(
        queryset=Avatar.objects.all(),
        widget=forms.RadioSelect, # Tampilkan sebagai pilihan radio
        empty_label=None, # Tidak ada pilihan kosong
        label="Pilih Avatar Baru"
    )