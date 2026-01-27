from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Client,
    Vehicule,
    Service,
    Chauffeur,
    Reclamation,
    Incident,
    Agent,
    Package,
    Shipment,
    Tour,
    Invoice,
)

admin.site.register(Client)
admin.site.register(Vehicule)
admin.site.register(Service)
admin.site.register(Chauffeur)
admin.site.register(Reclamation)
admin.site.register(Incident)
admin.site.register(Agent)
admin.site.register(Package)
admin.site.register(Shipment)
admin.site.register(Tour)
admin.site.register(Invoice)

