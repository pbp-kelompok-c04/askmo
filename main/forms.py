from django.forms import ModelForm
from main.models import Lapangan, Coach, Event


class LapanganForm(ModelForm):
    class Meta:
        model = Lapangan
        fields = ["nama", "deskripsi", "olahraga", "thumbnail", "rating", "refund", "tarif_per_sesi", "kontak", "alamat", "review", "peraturan", "fasilitas"]

class CoachForm(ModelForm):
    class Meta:
        model = Coach
        fields = ["nama", "olahraga", "deskripsi", "kontak", "tarif_per_jam", "thumbnail"]

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["nama", "deskripsi", "olahraga", "tanggal", "lokasi", "kontak", "thumbnail", "jam", "biaya"]