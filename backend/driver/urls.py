from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='driver_index'),
    # dashboard route expected by frontend
    path('dashboard/', views.index, name='driver_dashboard'),
]
