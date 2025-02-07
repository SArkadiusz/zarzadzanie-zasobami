"""
URL configuration for zarzadzanie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from zasoby import views
urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/add/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('addcategory/', views.add_category, name='add_category'),
    path('history/', views.history_list, name='history_list'),
    path('resources/<int:resource_id>/add_history/', views.add_history, name='add_history'),
    path('report/', views.generate_report, name='generate_report'),
    path('chart-data/', views.chart_data, name='chart_data'),
    path('category_usage_chart/', views.category_usage_chart, name='category_usage_chart'),
    path('statistics/', views.statistics_view, name='statistics'),
    path("pdf/", views.generate_pdf_view, name="generate_pdf_view"),
    path("pdf/download/", views.generate_pdf, name="generate_pdf"),
    path('expiring-soon/', views.expiring_soon_resources, name='expiring_soon_resources'),
]