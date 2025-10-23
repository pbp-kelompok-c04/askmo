from django.forms import ModelForm
from django import forms
from main.models import Lapangan, Coach, Event
from review.models import Review


class LapanganForm(ModelForm):
    class Meta:
        model = Lapangan
        fields = ["nama", "deskripsi", "olahraga", "thumbnail", "rating", "refund", "tarif_per_sesi", "kontak", "alamat", "review", "peraturan", "fasilitas"]

    def clean_rating(self):
        rating = self.cleaned_data.get("rating",0.0)
        if not (0.0 <= rating <= 5.0):
            raise forms.ValidationError("Rating harus antara 0.0 sampai 5.0")
        return rating
        


class CoachForm(ModelForm):
    class Meta:
        model = Coach
        fields = ["nama", "olahraga", "deskripsi", "kontak", "tarif_per_jam", "thumbnail"]

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["nama", "deskripsi", "olahraga", "tanggal", "lokasi", "kontak", "thumbnail", "jam"]

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
        fields = ["reviewer_name", "rating", "review_text", "gambar"]
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'placeholder': 'Masukkan Nama Anda'}),
            'review_text': forms.Textarea(attrs={'placeholder': 'Masukkan review Anda'}),
            'gambar': forms.URLInput(attrs={'placeholder': 'Masukkan URL gambar (opsional)'}),
        }
        labels = {
            'reviewer_name': 'Nama Anda',
            'review_text': 'Masukan dan Saran Anda',
            'gambar': 'Gambar (URL)',
        }