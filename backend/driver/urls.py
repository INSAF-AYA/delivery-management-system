from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='driver_index'),
    # dashboard route expected by frontend
    path('dashboard/', views.index, name='driver_dashboard'),
    # Driver auth endpoint (moved from /api/auth/driver/login/)
    path('auth/driver/login/', views.driver_login, name='driver_auth_login'),
]
