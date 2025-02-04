from django.contrib import admin
from .models import Category, Resource, History
from django.contrib import messages

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit', 'purchase_date', 'expiration_date')
    actions = ["send_notifications"]

    def send_notifications(self, request, queryset):
        for resource in queryset:
            resource.check_expiration_and_stock()
        messages.success(request, "Powiadomienia e-mail zostały wysłane!")

    send_notifications.short_description = "Wyślij powiadomienia e-mail"

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('resource', 'quantity_used', 'date_used')
