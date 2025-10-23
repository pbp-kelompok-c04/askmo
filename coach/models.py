from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Coach(models.Model):
    name = models.CharField(max_length=100)
    sport_branch = models.CharField(max_length=50, help_text="Example: Futsal, Badminton, Basketball")
    location = models.CharField(max_length=100, help_text="Example: South Jakarta")
    contact = models.CharField(max_length=50, help_text="Phone Number or Email")
    experience = models.TextField(blank=True, help_text="Briefly describe the coaching experience")
    certifications = models.TextField(blank=True, help_text="List certifications, separated by commas")
    service_fee = models.CharField(max_length=100, blank=True, help_text="Example: IDR 300,000 / hour")
    photo = models.ImageField(upload_to='coach_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.sport_branch}"

class CoachWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coach') 
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.coach.name}"