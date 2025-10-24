# main/forms.py
from django.forms import ModelForm
from django import forms
from coach.models import User
from main.models import Avatar, Lapangan, Coach, Event, UserProfile
from review.models import Review, ReviewCoach
from django.contrib.auth.forms import UserCreationForm


class LapanganForm(ModelForm):
    class Meta:
        model = Lapangan
        fields = ["nama", "deskripsi", "olahraga", "thumbnail", "rating", "refund", "tarif_per_sesi", "kontak", "alamat", "review", "peraturan", "fasilitas"]

    def clean_rating(self):
        # Meskipun rating di-exclude, jika field ini ada di form lain, validasi ini bisa berguna
        rating = self.cleaned_data.get("rating", 0.0)
        if rating is not None and not (0.0 <= rating <= 5.0):
            raise forms.ValidationError("Rating harus antara 0.0 sampai 5.0")
        return rating
        


class CoachForm(ModelForm):
    class Meta:
        model = Coach
        fields = ["nama", "olahraga", "deskripsi", "kontak", "tarif_per_jam", "thumbnail"]


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["nama", "deskripsi", "olahraga", "tanggal", "lokasi", "kontak", "thumbnail", "jam", "biaya"]

# Form BARU untuk Review
class ReviewForm(ModelForm):
    rating = forms.DecimalField(
        label="Rating (0.0 - 5.0)",
        min_value=0.0,
        max_value=5.0,
        decimal_places=1,
        widget=forms.NumberInput(attrs={'step': '0.1', 'min': '0.0', 'max': '5.0'})
    )
    
    # Tambahkan field untuk nama reviewer
    reviewer_name = forms.CharField(max_length=255)

    class Meta:
        model = Review
        fields = ["reviewer_name", "rating", "review_text", "gambar"]  # ⭐ INI YANG BENAR!
       
        widgets = {
            'review_text': forms.Textarea(attrs={'placeholder': 'Masukkan review Anda'}),
            'gambar': forms.URLInput(attrs={'placeholder': 'Masukkan URL gambar (opsional)'}),
        }
        labels = {
            'reviewer_name': 'Nama Anda',
            'review_text': 'Masukan dan Saran Anda',
            'gambar': 'Gambar (URL)',
        }


from django import forms


class ReviewCoachForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-5',
            'min': '1',
            'max': '5'
        })
    )
   
    class Meta:
        model = ReviewCoach
        fields = ['reviewer_name', 'rating', 'review_text']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama Anda'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Bagikan pengalaman Anda dengan coach ini...',
                'rows': 4
            }),
        }
        labels = {
            'reviewer_name': 'Nama Anda',
            'rating': 'Rating (1-5)',
            'review_text': 'Review',
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