from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'datepicker'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Resource
        fields = ['name', 'category', 'quantity', 'unit', 'purchase_date', 'expiration_date']
