from django.http import JsonResponse
import logging
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from database.models import Client, Chauffeur
from database.models import Package, Shipment, Expedition
from django.views.decorators.http import require_GET
from django.utils.dateformat import format as dateformat
from django.core.serializers.json import DjangoJSONEncoder
import json


@require_POST
def client_login(request):
    """Authenticate a Client via POST form (email, password).

    Returns JSON { success: true, role: 'client' } on success,
    otherwise returns 401/400 with success=false.
    """
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'error': 'missing_fields'}, status=400)

    try:
        client = Client.objects.get(email=email)
    except Client.DoesNotExist:
        return JsonResponse({'success': False}, status=401)

    if client.check_password(password):
        # Minimal session handling
        request.session['role'] = 'client'
        request.session['user_id'] = client.id_client
        return JsonResponse({'success': True, 'role': 'client'})

    return JsonResponse({'success': False}, status=401)


@require_POST
def driver_login(request):
    """Authenticate a Chauffeur (driver) via POST form.
    Returns JSON { success: true, role: 'driver' } on success.
    """
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'error': 'missing_fields'}, status=400)

    try:
        driver = Chauffeur.objects.get(email=email)
    except Chauffeur.DoesNotExist:
        return JsonResponse({'success': False}, status=401)

    if driver.check_password_driver(password):
        request.session['role'] = 'driver'
        request.session['user_id'] = driver.id_chauffeur
        return JsonResponse({'success': True, 'role': 'driver'})

    return JsonResponse({'success': False}, status=401)


@require_GET
def track(request):
    """Return basic tracking information for a package.

    Query param: number (tracking number)
    Response JSON structure (example):
    {
      "tracking": "SW123456789",
      "status": "In Transit",
      "estimated_delivery": "2025-12-30",
      "progress": 60,
      "events": [ {"description": "Package created", "date": "2025-12-20T12:34:56"}, ... ]
    }
    """
    # Accept either 'number' or 'tracking' as query param to be forgiving
    number = request.GET.get('number') or request.GET.get('tracking')
    logging.getLogger('api.track').info('Track request received, params=%s', request.GET.dict())
    print(f"[api.track] request.GET={request.GET.dict()}")
    if not number:
        return JsonResponse({'error': 'missing_number'}, status=400)

    try:
        pkg = Package.objects.get(tracking_number=number)
    except Package.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    # Try to get related shipment (one-to-one)
    shipment = None
    try:
        shipment = pkg.shipment
    except Shipment.DoesNotExist:
        shipment = None

    # Try to find an Expedition linked to the same client (best-effort)
    expedition = Expedition.objects.filter(client=pkg.client).order_by('-date_creation').first()

    # Build response
    events = []
    if pkg.date_creation:
        events.append({
            'description': 'Package created',
            'date': pkg.date_creation.isoformat()
        })

    if shipment:
        ev_date = shipment.shipment_date.isoformat() if shipment.shipment_date else shipment.date_creation.isoformat()
        events.append({
            'description': 'Shipment record created',
            'date': ev_date
        })

    if expedition:
        events.append({
            'description': f'Latest expedition status: {expedition.statut}',
            'date': expedition.date_creation.isoformat()
        })

    # Simple status/progress heuristic
    if expedition and expedition.statut == 'DELIVERED':
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
        'client': {
            'id': pkg.client.id_client,
            'email': pkg.client.email,
        }
    }

    return JsonResponse(response, encoder=DjangoJSONEncoder)
