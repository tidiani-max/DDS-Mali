from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Setup initial site data and superuser'

    def handle(self, *args, **kwargs):
        from django.core.management import call_command
        self.stdout.write('Loading fixtures...')
        call_command('loaddata', 'core/fixtures/initial_data.json')
        call_command('loaddata', 'scholarships/fixtures/initial_scholarships.json')
        call_command('loaddata', 'webinars/fixtures/initial_webinars.json')

        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@dds-mali.com', 'dds2026admin')
            self.stdout.write(self.style.SUCCESS('✅ Superuser created: admin / dds2026admin'))
        else:
            self.stdout.write('ℹ️  Superuser already exists')
        self.stdout.write(self.style.SUCCESS('✅ Site setup complete!'))
