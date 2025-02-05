from django.shortcuts import render, redirect, get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Resource, History, Category
from .forms import ResourceForm
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
import csv
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from datetime import date
import os
from django.conf import settings
def home_view(request):
    return render(request, 'zasoby/base.html')
def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'zasoby/resource_list.html', {'resources': resources})

def history_list(request):
    histories = History.objects.all()
    return render(request, 'zasoby/history_list.html', {'histories': histories})


# Widok dodawania zasobu
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'zasoby/resource_form.html', {'form': form})

# Widok edycji zasobu
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

# Widok usuwania zasobu
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.delete()
        return redirect('resource_list')
    return render(request, 'zasoby/resource_confirm_delete.html', {'resource': resource})


def generate_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resources_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Quantity', 'Unit', 'Purchase Date', 'Expiration Date'])

    for resource in Resource.objects.all():
        writer.writerow([resource.name, resource.category.name, resource.quantity, resource.unit,
                         resource.purchase_date, resource.expiration_date])

    return response


def chart_data(request):
    categories = Category.objects.all()
    data = {
        "labels": [category.name for category in categories],
        "values": [Resource.objects.filter(category=category).count() for category in categories]
    }
    return JsonResponse(data)

def history_chart_data(request):
    data = (
        History.objects.values("date_used")
        .annotate(total_used=Sum("quantity_used"))
        .order_by("date_used")
    )

    labels = [entry["date_used"].strftime("%Y-%m-%d") for entry in data]
    values = [entry["total_used"] for entry in data]

    return JsonResponse({"labels": labels, "values": values})

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
    option = request.GET.get("option", "all")  # Domyślnie pobiera wszystkie zasoby

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
        resources = Resource.objects.filter(quantity__lte=5)
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

# class ResourceUpdateView(UpdateView):
#     model = Resource
#     fields = ['name', 'category', 'quantity', 'unit', 'purchase_date', 'expiration_date']
#     template_name = 'zasoby/resource_form.html'
#     success_url = reverse_lazy('resource_list')
#
# class ResourceDeleteView(DeleteView):
#     model = Resource
#     template_name = 'zasoby/resource_confirm_delete.html'
#     success_url = reverse_lazy('resource_list')
#
# class HistoryUpdateView(UpdateView):
#     model = History
#     fields = ['resource', 'quantity_used', 'date_used']
#     template_name = 'zasoby/history_form.html'
#     success_url = reverse_lazy('history_list')
#
# class HistoryDeleteView(DeleteView):
#     model = History
#     template_name = 'zasoby/history_confirm_delete.html'
#     success_url = reverse_lazy('history_list')
