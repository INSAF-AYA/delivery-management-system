import os
import django
import sys

# ensure we're running from backend folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from database.models import Shipment, Package, Client

print('Listing last 50 Shipments with client info:')
print('-' * 80)
for sh in Shipment.objects.all().order_by('-date_creation')[:50]:
    pkg = getattr(sh, 'package', None)
    pkg_client = pkg.client.id_client if pkg and pkg.client else None
    sh_client = sh.client.id_client if sh.client else None
    print(f"Shipment: {sh.id_shipment}\n  shipment.client: {sh_client}\n  package.tracking: {pkg.tracking_number if pkg else 'N/A'}\n  package.client: {pkg_client}\n  statut: {sh.statut}\n  date_creation: {sh.date_creation}\n")

# Summarize any shipments that lack client on shipment but have it on package
print('\nSummary: shipments where shipment.client is null but package.client is present:')
for sh in Shipment.objects.filter(client__isnull=True).filter(package__client__isnull=False)[:50]:
    print(f"  {sh.id_shipment} -> package.client={sh.package.client.id_client} ({sh.package.client.email})")

# Count per client
from django.db.models import Count
print('\nShipment counts per client (derived from package):')
counts = Shipment.objects.values('package__client__id_client').annotate(count=Count('id_shipment')).order_by('-count')
for row in counts:
    print(row)

print('\nDone.')
