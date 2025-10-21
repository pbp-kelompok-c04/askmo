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
 

class Review(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=255, default="Anonim") # Nama reviewer diinput manual
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0) # 0.0 - 5.0
    review_text = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    gambar = models.URLField(blank=True, null=True) 
    
    class Meta:
        ordering = ['-tanggal_dibuat']

    def __str__(self):
        return f'Review oleh {self.reviewer_name} untuk {self.lapangan.nama} - Rating: {self.rating}'