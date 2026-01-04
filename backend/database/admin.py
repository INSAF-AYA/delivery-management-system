from django.contrib import admin

# Register your models here.
from .models import Package, Shipment, Tour, Invoice

admin.site.register(Package)
admin.site.register(Shipment)
admin.site.register(Tour)
admin.site.register(Invoice)
