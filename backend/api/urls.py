from django.urls import path
from . import views

urlpatterns = [
    path('auth/client/login/', views.client_login, name='api_client_login'),
    path('auth/driver/login/', views.driver_login, name='api_driver_login'),
    path('track/', views.track, name='api_track'),
  
]
