from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates admin users for the ASKMO team from the README'

    def handle(self, *args, **kwargs):
        admins = [
            {'name': 'Syafiq Faqih'},
            {'name': 'Ahmad Fauzan Al Ayubi'},
            {'name': 'Lessyarta Kamali Sopamena Pirade'},
            {'name': 'Matthew Wijaya'},
            {'name': 'Nisrina Alya Nabilah'},
            {'name': 'Farrell Zidane'}, # Asdos keren
        ]

        password = 'askmopasswordc04' 

        for admin_data in admins:
            full_name = admin_data['name']
            username = full_name.lower().replace(' ', '.')

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping.'))
                continue
            
            User.objects.create_user(
                username=username,
                password=password,
                first_name=full_name.split(' ')[0],
                is_staff=True 
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {username}'))

        self.stdout.write(self.style.SUCCESS(f'\nAll admin accounts created. The password for all users is: {password}'))