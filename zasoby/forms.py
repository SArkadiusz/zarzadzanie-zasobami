from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'category', 'quantity', 'unit', 'purchase_date', 'expiration_date']
