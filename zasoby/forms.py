from django import forms
from .models import Resource, History

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'category', 'quantity', 'unit', 'purchase_date', 'expiration_date']

class HistoryForm(forms.ModelForm):
    class Meta:
        model = History
        fields = ['quantity_used']
        labels = {
            'quantity_used': 'Ilość zużyta',
        }

    def __init__(self, *args, **kwargs):
        self.resource = kwargs.pop('resource', None)  # Pobieramy resource z kwargs
        super().__init__(*args, **kwargs)

    def clean_quantity_used(self):
        quantity_used = self.cleaned_data['quantity_used']
        if self.resource and quantity_used > self.resource.quantity: # Sprawdzamy, czy resource istnieje
            raise forms.ValidationError("Nie można zużyć więcej niż dostępna ilość.")
        return quantity_used