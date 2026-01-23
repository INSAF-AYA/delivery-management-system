from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.serializers.json import DjangoJSONEncoder
import logging

from database.models import Client, Package, Shipment


def client(request):
    return render(request, 'client.html')


@require_POST
def client_login(request):
    """Authenticate a Client via POST form (email, password)."""
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'error': 'missing_fields'}, status=400)

    try:
        client = Client.objects.get(email=email)
    except Client.DoesNotExist:
        return JsonResponse({'success': False}, status=401)

    if client.check_password(password):
        request.session['role'] = 'client'
        request.session['user_id'] = client.id_client
        return JsonResponse({'success': True, 'role': 'client'})

    return JsonResponse({'success': False}, status=401)


@require_GET
def track(request):
    """Return basic tracking information for a package (moved to client app)."""
    number = request.GET.get('number') or request.GET.get('tracking')
    logging.getLogger('api.track').info('Track request received, params=%s', request.GET.dict())
    if not number:
        return JsonResponse({'error': 'missing_number'}, status=400)

    try:
        pkg = Package.objects.get(tracking_number=number)
    except Package.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    shipment = None
    try:
        shipment = pkg.shipment
    except Shipment.DoesNotExist:
        shipment = None

    latest_shipment_for_client = Shipment.objects.filter(package__client=pkg.client).order_by('-date_creation').first()

    events = []
    if pkg.date_creation:
        events.append({'description': 'Package created', 'date': pkg.date_creation.isoformat()})

    if shipment:
        ev_date = shipment.shipment_date.isoformat() if shipment.shipment_date else shipment.date_creation.isoformat()
        events.append({'description': 'Shipment record created', 'date': ev_date})

    if latest_shipment_for_client:
        events.append({'description': f'Latest shipment status: {latest_shipment_for_client.statut}', 'date': latest_shipment_for_client.date_creation.isoformat()})

    if latest_shipment_for_client and latest_shipment_for_client.statut == 'DELIVERED':
        status = 'Delivered'
        progress = 100
    elif shipment:
        status = 'In Transit'
        progress = 60
    else:
        status = 'Created'
        progress = 5

    response = {
        'tracking': pkg.tracking_number,
        'status': status,
        'estimated_delivery': shipment.shipment_date.isoformat() if shipment and shipment.shipment_date else None,
        'progress': progress,
        'events': events,
        'client': {'id': pkg.client.id_client, 'email': pkg.client.email}
    }

    return JsonResponse(response, encoder=DjangoJSONEncoder)
