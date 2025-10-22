from main.models import Avatar, UserProfile
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage


Avatar.objects.get_or_create(id=5, defaults={'name': 'Default User', 'image_url': staticfiles_storage.url('avatar/default_avatar.png')})
print("Default avatar path confirmed.")

Avatar.objects.get_or_create(id=1, defaults={'name': 'Avatar 1', 'image_url': staticfiles_storage.url('avatar/avatar1.png')})
Avatar.objects.get_or_create(id=2, defaults={'name': 'Avatar 1', 'image_url': staticfiles_storage.url('avatar/avatar2.png')})
Avatar.objects.get_or_create(id=3, defaults={'name': 'Avatar 1', 'image_url': staticfiles_storage.url('avatar/avatar3.png')})
Avatar.objects.get_or_create(id=4, defaults={'name': 'Avatar 1', 'image_url': staticfiles_storage.url('avatar/avatar4.png')})



default_avatar = Avatar.objects.get(id=5)
for user in User.objects.all():
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created or not profile.avatar: 
        profile.avatar = default_avatar
        profile.save()
        print(f"Set default avatar for {user.username}")

exit()