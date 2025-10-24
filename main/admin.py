# Register your models here.
from django.contrib import admin
from .models import Lapangan, Collection, UserProfile, Avatar, Event, Coach

# Register your models here.
admin.site.register(Lapangan)
admin.site.register(Event)
admin.site.register(Collection)
admin.site.register(UserProfile)
admin.site.register(Avatar)
admin.site.register(Coach)