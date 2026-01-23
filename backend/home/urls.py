from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Login routes (named at top-level so templates can reverse without namespace)
    path('login/', views.login, name='login'),
    path('login/agent/', views.login_agent, name='login_agent'),
    path('login/client/', views.login_client, name='login_client'),
    path('login/driver/', views.login_driver, name='login_driver'),
    # Logout (clears session)
    path('logout/', views.logout_view, name='logout'),
    # Agent/auth login endpoint used by frontend (moved from /api/auth/login/)
    path('auth/login/', views.agent_login, name='agent_auth_login'),
]
