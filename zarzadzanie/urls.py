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
from zasoby.views import generate_report, home_view, chart_data, statistics_view, history_chart_data, category_usage_chart, generate_pdf_view, generate_pdf

urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/add/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('history/', views.history_list, name='history_list'),
    path('report/', generate_report, name='generate_report'),
    path('chart-data/', chart_data, name='chart_data'),
    path('history_chart/', history_chart_data, name='history_chart_data'),
    path('category_usage_chart/', category_usage_chart, name='category_usage_chart'),
    path('statistics/', statistics_view, name='statistics'),
    path("pdf/", generate_pdf_view, name="generate_pdf_view"),
    path("pdf/download/", generate_pdf, name="generate_pdf"),
]
