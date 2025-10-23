from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Coach(models.Model):
    name = models.CharField(max_length=100)
    sport_branch = models.CharField(max_length=50, help_text="Contoh : Sepak Bola, Futsal, Padel")
    location = models.CharField(max_length=100, help_text="Contoh : Jakarta Selatan, Bandung")
    contact = models.CharField(max_length=50, help_text="Nomor Telepon atau Email")
    experience = models.TextField(blank=True, help_text="Deskripsikan pengalaman Coach")
    certifications = models.TextField(blank=True, help_text="Sertifikat yang dimiliki oleh Coach, dipisah oleh koma")
    service_fee = models.CharField(max_length=100, blank=True, help_text="Contoh : RP 300,000 / Jam")
    photo = models.ImageField(upload_to='coach_photos/', blank=True, null=True)


    def __str__(self):
        return f"{self.name} - {self.sport_branch}"
   
    def calculate_average_rating(self):
        reviews = self.reviews.all()
        if reviews.count() > 0:
            avg = sum(review.rating for review in reviews) / reviews.count()
            return round(avg, 1)
        return None  # Return None jika belum ada review
   
    def get_average_rating_display(self):
        avg = self.calculate_average_rating()
        if avg is None:
            return "Belum ada review"
        # Ganti titik dengan koma
        return str(avg).replace('.', ',')
   
    def get_total_reviews(self):
        return self.reviews.count()
   
    def get_total_reviews_display(self):
        total = self.get_total_reviews()
        if total == 0:
            return "Belum ada review"
        return f"{total} review"


class CoachWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user', 'coach')
        ordering = ['-added_at']
   
    def __str__(self):
        return f"{self.user.username} - {self.coach.name}"
