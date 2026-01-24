from django.urls import path
from . import views

urlpatterns = [
    # Matches /client/ -> client.views.client
    path('', views.client, name='client'),
    # Direct routes to show specific tabs in the client portal
    path('shipments/', views.my_shipments, name='client_shipments'),
    path('invoices/', views.invoices, name='client_invoices'),
    path('support/', views.support, name='client_support'),
    # dashboard route expected by frontend
    path('dashboard/', views.client, name='client_dashboard'),
    # Track endpoint used by frontend (moved from /api/track/)
    path('track/', views.track, name='client_track'),
    # Client auth endpoint (moved from /api/auth/client/login/)
    path('auth/client/login/', views.client_login, name='client_auth_login'),
]
