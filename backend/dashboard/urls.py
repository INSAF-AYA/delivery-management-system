from django.urls import path
from . import views

urlpatterns = [
    # Keep the canonical name 'dashboard' so templates that reverse 'dashboard'
    # continue to work.
    path('', views.index, name='dashboard'),
    path('clients/', views.dashboard_clients, name='dashboard_clients'),
    path('shipments/', views.dashboard_shipments, name='dashboard_shipments'),
    path('drivers/', views.drivers, name='dashboard_drivers'),
    path('vehicles/', views.vehicles, name='dashboard_vehicles'),
    path('invoices/', views.invoices, name='dashboard_invoices'),
    path('incidents/', views.incidents, name='dashboard_incidents'),
]
