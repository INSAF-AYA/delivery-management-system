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

# Determine whether Shipment model includes an 'is_blocked' field. Some
# deployments/migrations may not have that field; handle gracefully so the
# admin doesn't crash during system checks.
try:
    _HAS_IS_BLOCKED = Shipment._meta.get_field('is_blocked') is not None
except Exception:
    _HAS_IS_BLOCKED = False


@admin.action(description='Mark selected shipments as blocked')
def block_shipments(modeladmin, request, queryset):
    if not _HAS_IS_BLOCKED:
        modeladmin.message_user(request, "Blocking not available: 'is_blocked' field is missing.")
        return
    updated = queryset.update(is_blocked=True)
    modeladmin.message_user(request, f"{updated} shipment(s) blocked.")


@admin.action(description='Unblock selected shipments')
def unblock_shipments(modeladmin, request, queryset):
    if not _HAS_IS_BLOCKED:
        modeladmin.message_user(request, "Unblocking not available: 'is_blocked' field is missing.")
        return
    updated = queryset.update(is_blocked=False)
    modeladmin.message_user(request, f"{updated} shipment(s) unblocked.")


class ShipmentAdmin(admin.ModelAdmin):
    # Build display/filter lists depending on whether is_blocked exists
    if _HAS_IS_BLOCKED:
        list_display = ('id_shipment', 'package', 'client', 'statut', 'is_blocked', 'date_creation')
        list_filter = ('statut', 'is_blocked')
        actions = [block_shipments, unblock_shipments]
    else:
        list_display = ('id_shipment', 'package', 'client', 'statut', 'date_creation')
        list_filter = ('statut',)
        actions = []


admin.site.register(Client)
admin.site.register(Vehicule)
admin.site.register(Service)
admin.site.register(Chauffeur)
admin.site.register(Reclamation)
admin.site.register(Incident)
admin.site.register(Agent)
admin.site.register(Package)
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Tour)
admin.site.register(Invoice)

