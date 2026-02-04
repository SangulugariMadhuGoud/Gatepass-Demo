"""
Django management command to create default superadmin account.
Creates superadmin with username 'Puppy' and password 'Charan@0709'
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates default superadmin account: username "Puppy", password "Charan@0709"'

    def handle(self, *args, **options):
        username = 'Puppy'
        email = 'puppy@hostel.com'
        password = 'Charan@0709'
        
        # Check if superadmin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superadmin "{username}" already exists. Skipping creation.')
            )
            return
        
        # Allow creating Puppy superadmin even if other superadmins exist
        # Only skip if Puppy already exists
        
        # Create superadmin
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='superadmin',
                is_staff=True,
                is_superuser=True,
                is_approved=True,  # Auto-approve superadmin
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created default superadmin "{username}" with email "{email}"'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Default credentials - Username: {username}, Password: {password}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superadmin: {str(e)}')
            )

