from django.urls import path
from . import views

app_name = 'invoice'

urlpatterns = [
    path('', views.invoice_list, name='list'),
    path('add/', views.invoice_add, name='add'),
    path('<str:invoice_id>/json/', views.invoice_detail_json, name='json'),
    path('<str:invoice_id>/delete/', views.invoice_delete, name='delete'),
    path('<str:invoice_id>/download/', views.invoice_download, name='download'),
    path('shipment-amounts/<str:shipment_id>/', views.shipment_amounts, name='shipment_amounts'),

]
