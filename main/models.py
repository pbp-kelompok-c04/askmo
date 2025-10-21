import uuid
from django.db import models
from django.contrib.auth.models import User

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
    deskripsi = models.TextField(blank=True, null=True)
    olahraga = models.CharField(max_length=20, choices=OLAHRAGA_CHOICES, default='update')
    thumbnail = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    refund = models.BooleanField(default=False)
    tarif_per_sesi = models.DecimalField(max_digits=10, decimal_places=2)

    alamat = models.TextField(blank=True, null=True)
    kecamatan = models.CharField(max_length=100, blank=True, null=True)
    kontak = models.CharField(max_length=100, blank=True, null=True)
    
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

class Avatar(models.Model):
    # Simpan URL/path ke gambar avatar
    name = models.CharField(max_length=50, unique=True)
    image_url = models.URLField(default='/static/avatar/default_avatar.png')

    def __str__(self):
        return self.name

# --- Model Profile yang terhubung ke User ---
class UserProfile(models.Model):
    OLAHRAGA_CHOICES = [
        ('sepakbola', 'Sepak Bola'),
        ('basket', 'Basket'),
        ('badminton', 'Badminton'),
        ('tenis', 'Tenis'),
        ('futsal', 'Futsal'),
        ('voli', 'Voli'),
        ('padel', 'Padel'),
        ('golf', 'Golf'),
        ('lainnya', 'Lainnya'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ForeignKey(
        Avatar, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    ) 

    olahraga_favorit = models.CharField(
        max_length=20, 
        choices=OLAHRAGA_CHOICES, 
        default='lainnya'
    )
    

    def __str__(self):
        return self.user.username
    
class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    lapangan = models.ManyToManyField(Lapangan, blank=True)
    coach = models.ManyToManyField(Coach, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
