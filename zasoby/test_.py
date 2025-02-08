import os
import pytest
from datetime import date
from django.utils.timezone import now
from django.test import Client
from django.urls import reverse
from django.db import transaction
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zarzadzanie.settings')
import django
django.setup()

from zasoby.models import Category, Resource, History
from zasoby.forms import ResourceForm, HistoryForm

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def category():
    return Category.objects.get_or_create(name="Testowa Kategoria")[0]

@pytest.fixture
def resource(category):
    return Resource.objects.create(
        name="Testowy Zasób",
        category=category,
        quantity=10,
        unit=Resource.UNIT_SZT,
        purchase_date=date(2023, 1, 1),
        expiration_date=date(2024, 1, 1)
    )

@pytest.fixture
def history(resource):
    return History.objects.create(resource=resource, quantity_used=2)

@pytest.mark.django_db
def test_category_creation(category):
    assert category.name == "Testowa Kategoria"
    assert str(category) == "Testowa Kategoria"

@pytest.mark.django_db
def test_resource_creation(resource, category):
    assert resource.name == "Testowy Zasób"
    assert resource.category == category
    assert resource.quantity == 10
    assert resource.unit == Resource.UNIT_SZT
    assert resource.purchase_date == date(2023, 1, 1)
    assert resource.expiration_date == date(2024, 1, 1)
    assert str(resource) == "Testowy Zasób (10.00 szt.)"

@pytest.mark.django_db
def test_history_creation(resource):
    history = History.objects.create(resource=resource, quantity_used=2)
    assert history.resource == resource
    assert history.quantity_used == 2
    assert history.date_used == now().date()
    assert str(history) == "Testowy Zasób - 2.00 szt. zużyte"

def test_home_view(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'zasoby/index.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_resource_list(client, resource):
    response = client.get(reverse('resource_list'))
    assert response.status_code == 200
    assert 'zasoby/resource_list.html' in [t.name for t in response.templates]
    assert resource in response.context['resources']

@pytest.mark.django_db
def test_history_list(client, history):
    response = client.get(reverse('history_list'))
    assert response.status_code == 200
    assert 'zasoby/history_list.html' in [t.name for t in response.templates]
    assert history in response.context['histories']

@pytest.mark.django_db
def test_add_history_get(client, resource):
    response = client.get(reverse('add_history', args=[resource.id]))
    assert response.status_code == 200
    assert 'zasoby/history_form.html' in [t.name for t in response.templates]
    assert isinstance(response.context['form'], HistoryForm)
    assert response.context['resource'] == resource

@pytest.mark.django_db
def test_add_history_post(client, resource):
    with transaction.atomic():
        initial_quantity = resource.quantity
        response = client.post(reverse('add_history', args=[resource.id]), {'quantity_used': 3})
        assert response.status_code == 302
        resource.refresh_from_db()
        assert resource.quantity == initial_quantity - 3
        assert History.objects.count() == 1

@pytest.mark.django_db
def test_resource_create_get(client):
    response = client.get(reverse('resource_create'))
    assert response.status_code == 200
    assert 'zasoby/resource_form.html' in [t.name for t in response.templates]
    assert isinstance(response.context['form'], ResourceForm)

@pytest.mark.django_db
def test_resource_create_post(client, category):
    response = client.post(reverse('resource_create'), {'name': 'Nowy Zasób', 'category': category.id, 'quantity': 5, 'unit': Resource.UNIT_SZT, 'purchase_date': '2024-01-01', 'expiration_date': '2025-01-01'})
    assert response.status_code == 302
    assert Resource.objects.count() == 1

@pytest.mark.django_db
def test_resource_edit_get(client, resource):
    response = client.get(reverse('resource_edit', args=[resource.id]))
    assert response.status_code == 200
    assert 'zasoby/resource_form.html' in [t.name for t in response.templates]
    assert isinstance(response.context['form'], ResourceForm)
    assert response.context['form'].instance == resource

@pytest.mark.django_db
def test_resource_edit_post(client, resource, category):
    response = client.post(reverse('resource_edit', args=[resource.id]), {'name': 'Zmieniony Zasób', 'category': category.id, 'quantity': 15, 'unit': Resource.UNIT_SZT, 'purchase_date': '2024-02-01', 'expiration_date': '2025-02-01'})
    assert response.status_code == 302
    updated_resource = Resource.objects.get(pk=resource.id)
    assert updated_resource.name == 'Zmieniony Zasób'
    assert updated_resource.quantity == 15

@pytest.mark.django_db
def test_resource_delete_get(client, resource):
    response = client.get(reverse('resource_delete', args=[resource.id]))
    assert response.status_code == 200
    assert 'zasoby/resource_confirm_delete.html' in [t.name for t in response.templates]
    assert response.context['resource'] == resource

@pytest.mark.django_db
def test_resource_delete_post(client, resource):
    response = client.post(reverse('resource_delete', args=[resource.id]))
    assert response.status_code == 302
    assert Resource.objects.count() == 0

@pytest.mark.django_db
def test_category_list(client, category):
    response = client.get(reverse('category_list'))
    assert response.status_code == 200
    assert 'zasoby/category_list.html' in [t.name for t in response.templates]
    assert category in response.context['categories']

@pytest.mark.django_db
def test_add_category_post(client):
    response = client.post(reverse('add_category'), {'name': 'Nowa Kategoria'})
    assert response.status_code == 302
    assert Category.objects.count() == 1

@pytest.mark.django_db
def test_chart_data(client, category, resource):
    response = client.get(reverse('chart_data'))
    assert response.status_code == 200
    data = response.json()
    assert category.name in data['labels']
    assert 1 in data['values']

def test_category_usage_chart(client, history):
    response = client.get(reverse('category_usage_chart'))
    assert response.status_code == 200
    data = response.json()
    assert history.resource.category.name in data['labels']
    assert str(sum(History.objects.filter(resource__category=history.resource.category).values_list('quantity_used', flat=True))) in data['values']

def test_statistics_view(client):
    response = client.get(reverse('statistics'))
    assert response.status_code == 200
    assert 'zasoby/statistics.html' in [t.name for t in response.templates]

def test_generate_pdf_view(client):
    response = client.get(reverse('generate_pdf_view'))
    assert response.status_code == 200
    assert 'zasoby/pdf_options.html' in [t.name for t in response.templates]

def test_resource_form_valid(category):
    form_data = {
        'name': 'Testowy Zasób',
        'category': category.id,
        'quantity': 5,
        'unit': Resource.UNIT_SZT,
        'purchase_date': '2023-01-01',
        'expiration_date': '2024-01-01',
    }
    form = ResourceForm(data=form_data)
    assert form.is_valid()

def test_resource_form_invalid_missing_fields(category):
    form_data = {
        'name': '',
        'category': category.id,
        'quantity': 5,
        'unit': Resource.UNIT_SZT,
        'purchase_date': '2024-01-01',
        'expiration_date': '2022-01-01',
    }
    form = ResourceForm(data=form_data)
    assert not form.is_valid()
    assert 'name' in form.errors

def test_resource_form_invalid_negative_quantity(category):
    form_data = {
        'name': 'Test',
        'category': category.id,
        'quantity': -1,
        'unit': Resource.UNIT_SZT,
        'purchase_date': '2024-01-01',
        'expiration_date': '2025-01-01',
    }
    form = ResourceForm(data=form_data)
    assert form.is_valid()



def test_history_form_valid(resource):
    form_data = {'quantity_used': 3}
    form = HistoryForm(data=form_data, resource=resource)
    assert form.is_valid()

def test_history_form_invalid_quantity(resource):
    form_data = {'quantity_used': 15}
    form = HistoryForm(data=form_data, resource=resource)
    assert not form.is_valid()
    assert 'quantity_used' in form.errors
    assert "Nie można zużyć więcej niż dostępna ilość." in form.errors['quantity_used']

def test_history_form_invalid_type():
    form_data = {'quantity_used': 'abc'}
    form = HistoryForm(data=form_data)
    assert not form.is_valid()
    assert 'quantity_used' in form.errors