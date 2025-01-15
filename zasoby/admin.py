from django.contrib import admin
from .models import Category, Resource, History

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit', 'purchase_date', 'expiration_date')

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('resource', 'quantity_used', 'date_used')