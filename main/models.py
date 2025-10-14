import uuid
from django.db import models

class Lapangan(models.Model):
    OLAHRAGA_CHOICES = [
        ('sepakbola', 'Sepak Bola'),
        ('basket', 'Basket'),
        ('voli', 'Voli'),
        ('badminton', 'Badminton'),
        ('tenis', 'Tenis'),
        ('futsal', 'Futsal'),
        ('padel', 'Padel'),
        ('golf', 'Golf'),
        ('lainnya', 'Lainnya'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    olahraga = models.CharField(max_length=20, choices=OLAHRAGA_CHOICES, default='update')
    thumbnail = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    refund = models.BooleanField(default=False)
    tarif_per_sesi = models.DecimalField(max_digits=10, decimal_places=2)
    kontak = models.CharField(max_length=100)
    alamat = models.TextField()
    kecamatan = models.CharField(max_length=100, blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    peraturan = models.TextField(blank=True, null=True)
    fasilitas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nama
    
class Coach(models.Model):
    OLAHRAGA_CHOICES = [
        ('sepakbola', 'Sepak Bola'),
        ('basket', 'Basket'),
        ('voli', 'Voli'),
        ('badminton', 'Badminton'),
        ('tenis', 'Tenis'),
        ('futsal', 'Futsal'),
        ('padel', 'Padel'),
        ('golf', 'Golf'),
        ('lainnya', 'Lainnya'),
    ]
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=255)
    olahraga = models.CharField(max_length=20, choices=OLAHRAGA_CHOICES, default='lainnya')
    deskripsi = models.TextField()
    kontak = models.CharField(max_length=100)
    tarif_per_jam = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.nama
    
class Event(models.Model):
    OLAHRAGA_CHOICES = [
        ('sepakbola', 'Sepak Bola'),
        ('basket', 'Basket'),
        ('voli', 'Voli'),
        ('badminton', 'Badminton'),
        ('tenis', 'Tenis'),
        ('futsal', 'Futsal'),
        ('padel', 'Padel'),
        ('golf', 'Golf'),
        ('lainnya', 'Lainnya'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=255)
    olahraga = models.CharField(max_length=20, choices=OLAHRAGA_CHOICES, default='update')
    deskripsi = models.TextField()
    tanggal = models.DateField()
    lokasi = models.CharField(max_length=255)
    kontak = models.CharField(max_length=100)
    biaya = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.URLField(blank=True, null=True)
    jam = models.TimeField(blank=True, null=True)
    
    def __str__(self):
        return self.nama