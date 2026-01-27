from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.serializers.json import DjangoJSONEncoder
import logging

from database.models import Client, Package, Shipment, Invoice, Reclamation
from django.db.models import Q


def client(request):
 
    return my_shipments(request)


def my_shipments(request):
 
    context = {'active_tab': 'shipments', 'shipments': [], 'stats': {}}

    try:
        role = request.session.get('role')
        user_id = request.session.get('user_id')
        if role != 'client' or not user_id:
            # not a logged-in client — render page but without shipments
            return render(request, 'client.html', context)

        # Load client and their shipments (via package relation)
        try:
            client_obj = Client.objects.get(pk=user_id)
        except Client.DoesNotExist:
            return render(request, 'client.html', context)

        # Include shipments linked either via the package.client or the shipment.client
        shipments_qs = Shipment.objects.filter(Q(package__client=client_obj) | Q(client=client_obj)).order_by('-date_creation')

        shipments = []
        for sh in shipments_qs:
            pkg = getattr(sh, 'package', None)
            tracking = pkg.tracking_number if pkg else ''
            # simple progress heuristic
            if sh.statut and sh.statut.upper() == 'DELIVERED':
                progress = 100
            elif sh.statut and sh.statut.upper() == 'IN_TRANSIT':
                progress = 60
            else:
                progress = 10

            shipments.append({
                'id_shipment': sh.id_shipment,
                'tracking': tracking,
                'origin': sh.origin,
                'destination': sh.destination,
                'status': sh.statut,
                'estimated_delivery': sh.shipment_date.isoformat() if sh.shipment_date else '',
                'progress': progress,
                'date_creation': sh.date_creation.isoformat() if sh.date_creation else '',
            })

        context['shipments'] = shipments
        # Build simple stats for the client
        try:
            active_count = shipments_qs.exclude(statut__iexact='DELIVERED').count()
            completed_count = shipments_qs.filter(statut__iexact='DELIVERED').count()
        except Exception:
            active_count = len([s for s in shipments if s.get('status') != 'DELIVERED'])
            completed_count = len([s for s in shipments if s.get('status') == 'DELIVERED'])

        # Pending invoices: best-effort count of invoices linked to the client
        try:
            pending_invoices = Invoice.objects.filter(client=client_obj).count()
        except Exception:
            pending_invoices = 0

        # Open tickets: use Reclamation as the support ticket model (project stores reclamations globally).
        # Note: Reclamation currently has no client FK in the schema, so this is a global open ticket count.
        try:
            open_tickets = Reclamation.objects.filter(status__in=['new', 'open', 'in_progress']).count()
        except Exception:
            open_tickets = 0

        context['stats'] = {
            'active_shipments': active_count,
            'completed_shipments': completed_count,
            'pending_invoices': pending_invoices,
            'open_tickets': open_tickets,
        }

        return render(request, 'client.html', context)
    except Exception:
        # On any unexpected error, log and return page without shipments
        logging.getLogger('client.my_shipments').exception('Error building shipments list')
        return render(request, 'client.html', context)


def invoices(request):
    """Render the client portal with the Invoices tab active."""
    context = {'active_tab': 'invoices', 'stats': {}}

    # attach stats when possible (same logic as my_shipments but lighter)
    try:
        role = request.session.get('role')
        user_id = request.session.get('user_id')
        if role == 'client' and user_id:
            client_obj = Client.objects.filter(pk=user_id).first()
            if client_obj:
                shipments_qs = Shipment.objects.filter(Q(package__client=client_obj) | Q(client=client_obj))
                context['stats'] = {
                    'active_shipments': shipments_qs.exclude(statut__iexact='DELIVERED').count(),
                    'completed_shipments': shipments_qs.filter(statut__iexact='DELIVERED').count(),
                    'pending_invoices': Invoice.objects.filter(client=client_obj).count(),
                    'open_tickets': Reclamation.objects.filter(status__in=['new', 'open', 'in_progress']).count(),
                }
    except Exception:
        pass

    return render(request, 'client.html', context)


def support(request):
    """Render the client portal with the Support tab active."""
    context = {'active_tab': 'support', 'stats': {}}
    try:
        role = request.session.get('role')
        user_id = request.session.get('user_id')
        if role == 'client' and user_id:
            client_obj = Client.objects.filter(pk=user_id).first()
            if client_obj:
                shipments_qs = Shipment.objects.filter(Q(package__client=client_obj) | Q(client=client_obj))
                context['stats'] = {
                    'active_shipments': shipments_qs.exclude(statut__iexact='DELIVERED').count(),
                    'completed_shipments': shipments_qs.filter(statut__iexact='DELIVERED').count(),
                    'pending_invoices': Invoice.objects.filter(client=client_obj).count(),
                    'open_tickets': Reclamation.objects.filter(status__in=['new', 'open', 'in_progress']).count(),
                }
    except Exception:
        pass

    return render(request, 'client.html', context)


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

    
    try:
        role = request.session.get('role')
        user_id = request.session.get('user_id')
        if role == 'client' and user_id is not None:
          
            try:
                if str(user_id) != str(pkg.client.id_client):
                    logging.getLogger('api.track').warning(
                        'Client %s attempted to access package %s owned by %s',
                        user_id, pkg.tracking_number, pkg.client.id_client
                    )
                    return JsonResponse({'error': 'forbidden'}, status=403)
            except Exception:
                # If any error occurs while comparing identifiers, deny access conservatively.
                logging.getLogger('api.track').exception('Error comparing session user id with package owner')
                return JsonResponse({'error': 'forbidden'}, status=403)
    except Exception:
        # Be conservative: if any error occurs while checking session, deny access
        logging.getLogger('api.track').exception('Error while authorizing track request')
        return JsonResponse({'error': 'forbidden'}, status=403)

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
