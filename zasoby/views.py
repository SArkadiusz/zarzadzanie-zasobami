from django.shortcuts import render
from .models import Resource, History

def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'zasoby/resource_list.html', {'resources': resources})

def history_list(request):
    histories = History.objects.all()
    return render(request, 'zasoby/history_list.html', {'histories': histories})
