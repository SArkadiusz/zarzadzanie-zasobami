from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Resource(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default="szt.")  # np. szt., kg, l
    purchase_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

class History(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    date_used = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} - {self.quantity_used} {self.resource.unit} zużyte"
