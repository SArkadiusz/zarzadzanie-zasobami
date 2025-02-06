from django.db import models
from datetime import date, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Resource(models.Model):

    UNIT_SZT = 'szt.'
    UNIT_KG = 'kg'
    UNIT_L = 'l'
    UNIT_OP = 'op.'

    UNIT_CHOICES = (
        (UNIT_SZT, 'szt.'),
        (UNIT_KG, 'kg'),
        (UNIT_L, 'L'),
        (UNIT_OP, 'op.'),
    )

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, default=UNIT_SZT)
    purchase_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    def check_expiration_and_stock(self):
        """Sprawdza datę ważności i ilość zasobu, wysyłając e-mail w razie potrzeby."""
        today = now().date()

        if self.expiration_date and self.expiration_date <= today + timedelta(days=7):
            self.send_email_alert("Data ważności produktu się kończy!")

        if self.quantity <= 1:
            self.send_email_alert("Zasób prawie się skończył!")

    def send_email_alert(self, message):
        """Wysyła powiadomienie e-mail."""
        send_mail(
            subject=f"Powiadomienie: {self.name}",
            message=f"{message}\n\nProdukt: {self.name}\nPozostała ilość: {self.quantity} {self.unit}\nData ważności: {self.expiration_date}",
            from_email="arkadinio@gmail.com",
            recipient_list=["arkadiniogry@gmail.com"],
            fail_silently=False,
        )

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

class History(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    date_used = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} - {self.quantity_used} {self.resource.unit} zużyte"
