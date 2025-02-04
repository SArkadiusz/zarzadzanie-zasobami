from django.core.management.base import BaseCommand
from zasoby.models import Resource

class Command(BaseCommand):
    help = "Sprawdza kończące się zasoby i wysyła powiadomienia e-mail"

    def handle(self, *args, **kwargs):
        for resource in Resource.objects.all():
            resource.check_expiration_and_stock()
        self.stdout.write(self.style.SUCCESS("Sprawdzono zasoby i wysłano powiadomienia, jeśli były potrzebne."))
