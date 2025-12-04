from django.db import models
from django.contrib.auth.models import User
from main.models import Lapangan


class Review(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=255, default="Anonim")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)  # 0.0 - 5.0
    review_text = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    gambar = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-tanggal_dibuat']

    def __str__(self):
        return f'Review oleh {self.reviewer_name} untuk {self.lapangan.nama} - Rating: {self.rating}'

    def can_edit(self, user, session_key=None):
        if user and user.is_authenticated:
            # Hanya pemilik akun atau admin
            if self.user and self.user == user:
                return True
            if user.is_staff:
                return True
            return False

        if session_key and self.session_key and self.session_key == session_key:
            return True

        return False

    def can_delete(self, user, session_key=None):
        return self.can_edit(user, session_key)

   
from django.db import models
from django.contrib.auth.models import User
from coach.models import Coach

class ReviewCoach(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    review_text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.coach.name} by {self.reviewer_name}"

    def can_edit(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.user == user or user.is_staff

    def can_delete(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.user == user or user.is_staff