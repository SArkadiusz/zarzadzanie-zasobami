from django.shortcuts import render, redirect, get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.db import transaction
from .models import Resource, History, Category
from .forms import ResourceForm, HistoryForm
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from reportlab.pdfgen import canvas
from datetime import date, timedelta
import os
from django.conf import settings
def home_view(request):
    return render(request, 'zasoby/index.html')

def resource_list(request):
    resources = Resource.objects.exclude(quantity=0)
    return render(request, 'zasoby/resource_list.html', {'resources': resources})

def history_list(request):
    histories = History.objects.all()
    return render(request, 'zasoby/history_list.html', {'histories': histories})

def add_history(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    if request.method == 'POST':
        form = HistoryForm(request.POST, resource=resource)
        if form.is_valid():
            with transaction.atomic():
                history = form.save(commit=False)
                history.resource = resource
                history.save()

                quantity_used = history.quantity_used
                resource.quantity -= quantity_used
                resource.save()

            return redirect('resource_list')
    else:
        form = HistoryForm(resource=resource)
    return render(request, 'zasoby/history_form.html', {'form': form, 'resource': resource})

def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'zasoby/resource_form.html', {'form': form})

def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            return redirect('resource_list')
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'zasoby/resource_form.html', {'form': form})

def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.delete()
        return redirect('resource_list')
    return render(request, 'zasoby/resource_confirm_delete.html', {'resource': resource})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'zasoby/category_list.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('category_list')
    return render(request, 'zasoby/add_category.html')

def chart_data(request):
    categories = Category.objects.all()
    data = {
        "labels": [category.name for category in categories],
        "values": [Resource.objects.filter(category=category).count() for category in categories]
    }
    return JsonResponse(data)

def category_usage_chart(request):
    data = (
        History.objects.values("resource__category__name")
        .annotate(total_used=Sum("quantity_used"))
        .order_by("-total_used")
    )

    labels = [entry["resource__category__name"] for entry in data]
    values = [entry["total_used"] for entry in data]

    return JsonResponse({"labels": labels, "values": values})

def statistics_view(request):
    return render(request, 'zasoby/statistics.html')

def generate_pdf_view(request):
    """Widok formularza wyboru opcji generowania PDF-a"""
    return render(request, "zasoby/pdf_options.html")

def generate_pdf(request):
    """Widok generujący PDF na podstawie wybranej opcji"""
    option = request.GET.get("option", "all")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="zasoby.pdf"'

    p = canvas.Canvas(response)

    font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    p.setFont("DejaVuSans", 14)
    p.drawString(100, 800, "Lista zasobów")

    y_position = 780

    if option == "all":
        resources = Resource.objects.all()
        p.drawString(100, y_position, "Wszystkie zasoby:")
    elif option == "expiring":
        resources = Resource.objects.filter(expiration_date__lte=date.today())
        p.drawString(100, y_position, "Zasoby z kończącą się datą ważności:")
    elif option == "low_stock":
        resources = Resource.objects.filter(quantity__lte=1)
        p.drawString(100, y_position, "Zasoby z niskim stanem:")
    else:
        p.drawString(100, y_position, "Niepoprawna opcja")
        p.showPage()
        p.save()
        return response

    for resource in resources:
        y_position -= 20
        p.drawString(100, y_position,
                     f"{resource.name} - {resource.quantity} {resource.unit} (Ważność: {resource.expiration_date})")

    p.showPage()
    p.save()
    return response

def expiring_soon_resources(request):
    today = date.today()
    next_week = today + timedelta(days=7)
    resources = Resource.objects.filter(expiration_date__lte=next_week, expiration_date__gte=today).exclude(quantity=0)
    return render(request, 'zasoby/expiring_soon_resources.html', {'resources': resources})