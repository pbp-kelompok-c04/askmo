from django.db import models

from main.models import Lapangan


class Review(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=255, default="Anonim")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0) # 0.0 - 5.0
    review_text = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    gambar = models.URLField(blank=True, null=True) 
    session_key = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-tanggal_dibuat']

    def __str__(self):
        return f'Review oleh {self.reviewer_name} untuk {self.lapangan.nama} - Rating: {self.rating}'
