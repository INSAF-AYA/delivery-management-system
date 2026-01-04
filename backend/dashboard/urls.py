from django.urls import path
from . import views

urlpatterns = [
    # Keep the canonical name 'dashboard' so templates that reverse 'dashboard'
    # continue to work.
    path('', views.index, name='dashboard'),
    path('clients/', views.dashboard_clients, name='dashboard_clients'),
    path('clients/<str:client_id>/json/', views.show_client, name='dashboard_show_client'),
    path('clients/<str:client_id>/edit/', views.edit_client, name='dashboard_edit_client'),
    path('clients/<str:client_id>/reset_password/', views.reset_client_password, name='dashboard_reset_client_password'),
    path('clients/<str:client_id>/delete/', views.delete_client, name='dashboard_delete_client'),
    path('shipments/', views.dashboard_shipments, name='dashboard_shipments'),
    path('drivers/', views.drivers, name='dashboard_drivers'),
    path('drivers/add/', views.add_driver, name='dashboard_add_driver'),
    path('drivers/<str:driver_id>/json/', views.show_driver, name='dashboard_show_driver'),
    path('drivers/<str:driver_id>/reset_password/', views.reset_driver_password, name='dashboard_reset_driver_password'),
    path('vehicles/', views.vehicles, name='dashboard_vehicles'),
    path('invoices/', views.invoices, name='dashboard_invoices'),
    path('incidents/', views.incidents, name='dashboard_incidents'),
     path('clients/add/', views.add_client, name='dashboard_add_client'),
]
