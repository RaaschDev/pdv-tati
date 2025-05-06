from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser with predefined credentials'

    def handle(self, *args, **options):
        if not User.objects.filter(username='Admin').exists():
            User.objects.create_superuser(
                username='Admin',
                password='rafa1254',
                email='admin@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists')) 