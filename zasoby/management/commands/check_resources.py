# from django.core.management.base import BaseCommand
# from zasoby.models import Resource
#
# class Command(BaseCommand):
#     help = "Sprawdza kończące się zasoby i wysyła powiadomienia e-mail"
#
#     def handle(self, *args, **kwargs):
#         for resource in Resource.objects.all():
#             resource.check_expiration_and_stock()
#         self.stdout.write(self.style.SUCCESS("Sprawdzono zasoby i wysłano powiadomienia, jeśli były potrzebne."))

from django.core.management.base import BaseCommand
from zasoby.models import Resource
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta


class Command(BaseCommand):
    help = "Sprawdza kończące się zasoby i wysyła zbiorcze powiadomienie e-mail"

    def handle(self, *args, **kwargs):
        today = now().date()
        low_stock_resources = []
        expiring_resources = []

        for resource in Resource.objects.all():
            if resource.expiration_date and resource.expiration_date <= today + timedelta(days=7):
                expiring_resources.append(resource)

            if resource.quantity <= 1:
                low_stock_resources.append(resource)

        if expiring_resources or low_stock_resources:
            self.send_bulk_email(expiring_resources, low_stock_resources)

        self.stdout.write(self.style.SUCCESS("Sprawdzono zasoby i wysłano powiadomienia, jeśli były potrzebne."))

    def send_bulk_email(self, expiring_resources, low_stock_resources):
        subject = "Powiadomienie: Kończące się zasoby"
        message = "Lista produktów wymagających uwagi:\n\n"

        if expiring_resources:
            message += "Produkty z kończącą się datą ważności:\n"
            for res in expiring_resources:
                message += f"- {res.name}, Data ważności: {res.expiration_date}\n"
            message += "\n"

        if low_stock_resources:
            message += "Produkty o niskim stanie magazynowym:\n"
            for res in low_stock_resources:
                message += f"- {res.name}, Pozostała ilość: {res.quantity} {res.unit}\n"

        send_mail(
            subject=subject,
            message=message,
            from_email="arkadinio@gmail.com",
            recipient_list=["arkadiniogry@gmail.com"],
            fail_silently=False,
        )