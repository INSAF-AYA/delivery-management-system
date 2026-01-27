from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='driver_index'),
    path('dashboard/', views.index, name='driver_dashboard'),
    path('claim/', views.claim_shipment, name='driver_claim'),
    path('update_status/', views.update_shipment_status, name='driver_update_status'),
]
