"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


# Also import the dashboard view so we can expose a top-level named route
from dashboard import views as dash_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect root to the home page
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),

    # App urlconfs
    path('', include('home.urls')),
    # Also expose the home app at /home/ so links to /home/ work
    path('home/', include('home.urls')),
    path('driver/', include('driver.urls')),
    # API endpoints (AJAX logins etc.)
    path('api/', include('api.urls')),

    # Provide a named top-level route 'dashboard' so templates that call
    # {% url 'dashboard' %} resolve correctly. Subpaths are handled by
    # including the dashboard.urls module.
    path('dashboard/', dash_views.index, name='dashboard'),
    path('dashboard/', include('dashboard.urls')),

    path('client/', include('client.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
