from django.forms import ModelForm
from django import forms
from main.models import Lapangan, Coach, Event


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