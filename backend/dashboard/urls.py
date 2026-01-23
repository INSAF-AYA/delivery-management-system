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
    path('clients/add/', views.add_client, name='dashboard_add_client'),
    
    # Shipments CRUD
    path('shipments/', views.dashboard_shipments, name='dashboard_shipments'),
    path('shipments/json/', views.list_shipments_json, name='dashboard_list_shipments'),
    path('shipments/add/', views.add_shipment, name='dashboard_add_shipment'),
    path('shipments/<str:shipment_id>/json/', views.show_shipment, name='dashboard_show_shipment'),
    path('shipments/<str:shipment_id>/edit/', views.edit_shipment, name='dashboard_edit_shipment'),
    path('shipments/<str:shipment_id>/delete/', views.delete_shipment, name='dashboard_delete_shipment'),
    
    # Incidents CRUD
    path('incidents/', views.incidents, name='dashboard_incidents'),
    path('incidents/json/', views.list_incidents_json, name='dashboard_list_incidents'),
    path('incidents/add/', views.add_incident, name='dashboard_add_incident'),
    path('incidents/<str:incident_id>/json/', views.show_incident, name='dashboard_show_incident'),
    path('incidents/<str:incident_id>/edit/', views.edit_incident, name='dashboard_edit_incident'),
    path('incidents/<str:incident_id>/delete/', views.delete_incident, name='dashboard_delete_incident'),
    
    # Drivers CRUD
    path('drivers/', views.drivers, name='dashboard_drivers'),
    path('drivers/add/', views.add_driver_ajax, name='dashboard_add_driver'),
    path('drivers/<str:driver_id>/json/', views.show_driver, name='dashboard_show_driver'),
    path('drivers/<str:driver_id>/edit/', views.edit_driver_ajax, name='dashboard_edit_driver'),
    path('drivers/<str:driver_id>/delete/', views.delete_driver_ajax, name='dashboard_delete_driver'),
    path('drivers/<str:driver_id>/reset_password/', views.reset_driver_password, name='dashboard_reset_driver_password'),
    
    # Vehicles CRUD
    path('vehicles/', views.vehicles, name='dashboard_vehicles'),
    path('vehicles/add/', views.add_vehicle, name='dashboard_add_vehicle'),
    path('vehicles/<str:vehicle_id>/json/', views.show_vehicle, name='dashboard_show_vehicle'),
    path('vehicles/<str:vehicle_id>/edit/', views.edit_vehicle, name='dashboard_edit_vehicle'),
    path('vehicles/<str:vehicle_id>/delete/', views.delete_vehicle, name='dashboard_delete_vehicle'),
    
    # Invoices CRUD
    path('invoices/', views.invoices, name='dashboard_invoices'),
    path('invoices/add/', views.add_invoice, name='dashboard_add_invoice'),
    path('invoices/<str:invoice_id>/json/', views.show_invoice, name='dashboard_show_invoice'),
    path('invoices/<str:invoice_id>/delete/', views.delete_invoice, name='dashboard_delete_invoice'),
    
    # Packages CRUD
    path('packages/', views.package, name='dashboard_packages'),
    path('packages/add/', views.add_package, name='dashboard_add_package'),
    path('packages/<str:package_id>/json/', views.show_package, name='dashboard_show_package'),
    path('packages/<str:package_id>/edit/', views.edit_package, name='dashboard_edit_package'),
    path('packages/<str:package_id>/delete/', views.delete_package, name='dashboard_delete_package'),
    
    # Agents CRUD
    path('agents/', views.agents, name='dashboard_agents'),
    path('agents/add/', views.add_agent, name='dashboard_add_agent'),
    path('agents/<str:agent_id>/json/', views.show_agent, name='dashboard_show_agent'),
    path('agents/<str:agent_id>/edit/', views.edit_agent, name='dashboard_edit_agent'),
    path('agents/<str:agent_id>/delete/', views.delete_agent, name='dashboard_delete_agent'),
]
