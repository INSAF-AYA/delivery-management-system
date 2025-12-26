from django.urls import path
from . import views

urlpatterns = [
    # Matches /client/ -> client.views.client
    path('', views.client, name='client'),
]
