from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Clears everything in db except users related tables'

    def handle(self, *args, **options):
        app = apps.app_configs.get('leaderboards')
        while True:
            user_input = input('Warning, this command will clear everything in database, continue? (y/n)')
            if user_input.lower() == 'y':
                for model_name, model in app.models.items():
                    model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted {model_name}'))
                break
            elif user_input.lower() == 'n':
                break
