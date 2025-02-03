from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource, History, Category
from .forms import ResourceForm
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
import csv
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
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
