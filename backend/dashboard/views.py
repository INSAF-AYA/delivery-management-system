from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import re
from datetime import datetime, date
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
import uuid
from django.db import IntegrityError

from database.models import Client, Chauffeur, Vehicule, Shipment, Incident, Package, Invoice, Agent
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from django.utils.timezone import make_aware

def dashboard_data(request):
    """Return JSON stats for dashboard"""
    total_shipments = Shipment.objects.count()
    total_drivers = Chauffeur.objects.count()
    total_clients = Client.objects.count()
    
    today = timezone.now().date()
    start_month = today.replace(day=1)
    
    monthly_revenue = (
        Invoice.objects.filter(invoice_date__gte=start_month)
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )

    return JsonResponse({
        "total_shipments": total_shipments,
        "total_drivers": total_drivers,
        "total_clients": total_clients,
        "monthly_revenue": float(monthly_revenue)
    })
  

def dashboard_charts_data(request):
    today = timezone.now().date()
    
    # Revenue trends (last 6 months)
    revenue_trends = []
    for i in range(6, 0, -1):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)  # trick to get last day
        month_end = month_end - timedelta(days=month_end.day)
        
        total = Invoice.objects.filter(
            invoice_date__gte=month_start,
            invoice_date__lte=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        revenue_trends.append({
            "month": month_start.strftime('%b %Y'),
            "revenue": float(total)
        })

    # Shipment status distribution
    status_distribution = Shipment.objects.values('statut').annotate(count=Count('id_shipment'))
    
    # Weekly delivery performance (last 7 days)
    weekly_performance = []
    for i in range(7, 0, -1):
        day = today - timedelta(days=i-1)
        count = Shipment.objects.filter(shipment_date=day).count()
        weekly_performance.append({
            "day": day.strftime('%a'),
            "count": count
        })
    
    return JsonResponse({
        "revenue_trends": revenue_trends,
        "status_distribution": list(status_distribution),
        "weekly_performance": weekly_performance
    })


def recent_activity_data(request):
    """
    Return recent activities:
    5 latest of each:
    clients, shipments, drivers, vehicles, invoices, packages, incidents, agents
    """

    activity_list = []

    # ---- Shipments ----
    shipments = Shipment.objects.select_related('client').order_by('-date_creation')[:5]
    for s in shipments:
        activity_list.append({
            "datetime": s.date_creation,
            "time": s.date_creation.strftime("%H:%M"),
            "action": "New Shipment",
            "user": f"{s.client.nom} {s.client.prenom}" if s.client else "Unknown",
            "details": f"Shipment #{s.id_shipment} created",
            "status": s.statut,
        })

    # ---- Incidents ----
    incidents = Incident.objects.order_by('-created_at')[:5]
    for i in incidents:
        activity_list.append({
            "datetime": i.created_at,
            "time": i.created_at.strftime("%H:%M"),
            "action": "Incident Reported",
            "user": "System",
            "details": i.description,
            "status": i.status,
        })

    # ---- Clients ----
    clients = Client.objects.order_by('-date_inscription')[:5]
    for c in clients:
        activity_list.append({
            "datetime": c.date_inscription,
            "time": c.date_inscription.strftime("%H:%M"),
            "action": "New Client",
            "user": f"{c.nom} {c.prenom}",
            "details": "Client registered",
            "status": "Completed",
        })

    # ---- Drivers ----
    drivers = Chauffeur.objects.order_by('-date_embauche')[:5]
    for d in drivers:
        activity_list.append({
            "datetime": d.date_embauche,
            "time": d.date_embauche.strftime("%H:%M"),
            "action": "New Driver",
            "user": f"{d.nom} {d.prenom}",
            "details": "Driver added to system",
            "status": d.statut,
        })

    # ---- Vehicles ----
    vehicles = Vehicule.objects.order_by('-date_mise_service')[:5]
    for v in vehicles:
        if not v.date_mise_service:
            continue
        activity_list.append({
            "datetime": v.date_mise_service,
            "time": v.date_mise_service.strftime("%H:%M"),
            "action": "Vehicle Added",
            "user": "System",
            "details": f"Vehicle {v.immatriculation}",
            "status": v.etat,
        })

    # ---- Invoices ----
    invoices = Invoice.objects.select_related('client').order_by('-invoice_date')[:5]
    for inv in invoices:
        activity_list.append({
            "datetime": inv.invoice_date,
            "time": inv.invoice_date.strftime("%H:%M"),
            "action": "Invoice Generated",
            "user": f"{inv.client.nom} {inv.client.prenom}" if inv.client else "Unknown",
            "details": f"Invoice #{inv.id_invoice}",
            "status": "Completed",
        })

    # ---- Packages ----
    packages = Package.objects.select_related('client').order_by('-date_creation')[:5]
    for p in packages:
        activity_list.append({
            "datetime": p.date_creation,
            "time": p.date_creation.strftime("%H:%M"),
            "action": "Package Created",
            "user": f"{p.client.nom} {p.client.prenom}" if p.client else "Unknown",
            "details": f"Tracking {p.tracking_number}",
            "status": "Completed",
        })

    # ---- Agents ----
    agents = Agent.objects.order_by('-agent_id')[:5]
    for a in agents:
        activity_list.append({
            "datetime": timezone.now(),  # no created_at → fallback
            "time": timezone.now().strftime("%H:%M"),
            "action": "Agent Added",
            "user": f"{a.nom} {a.prenom}",
            "details": f"Role: {a.role}",
            "status": "Active",
        })

    # ---- NORMALIZE DATETIME ----
    for act in activity_list:
        if isinstance(act["datetime"], datetime):
            continue
        # convert date → datetime
        act["datetime"] = make_aware(datetime.combine(act["datetime"], datetime.min.time()))

    # ---- SORT & CLEAN ----
    activity_list.sort(key=lambda x: x["datetime"], reverse=True)

    for act in activity_list:
        del act["datetime"]

    return JsonResponse({"activities": activity_list})


def _extract_marque_modele_from_type(type_vehicule):
    """Return (marque, modele) extracted from a stored type_vehicule string.

    The code encodes marque/modele as "<type> - <marque> <modele>" in several places
    for backward compatibility. This helper extracts those parts safely.
    """
    marque = ''
    modele = ''
    if not type_vehicule:
        return marque, modele
    if ' - ' in type_vehicule:
        _, rest = type_vehicule.split(' - ', 1)
        tokens = rest.split(' ', 1)
        marque = tokens[0] if tokens else ''
        modele = tokens[1] if len(tokens) > 1 else ''
    return marque, modele


def index(request):
    return render(request, 'DASHindex.html')

def agents(request):
    agents_list = Agent.objects.all().order_by('-agent_id')
    return render(request, 'agent.html', {
        'agents': agents_list,
    })


def show_agent(request, agent_id):
    """Return agent data as JSON for the view modal."""
    agent = get_object_or_404(Agent, pk=agent_id)
    data = {
        'agent_id': agent.agent_id,
        'nom': agent.nom,
        'prenom': agent.prenom,
        'email': agent.email,
        'telephone': agent.telephone,
        'role': agent.role,
    }
    return JsonResponse({'success': True, 'agent': data})


@require_POST
def add_agent(request):
    """Create a new agent."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        nom = payload.get('nom', '').strip()
        prenom = payload.get('prenom', '').strip()
        email = payload.get('email', '').strip()
        telephone = payload.get('telephone', '').strip()
        role = payload.get('role', 'agent').strip().lower()  # Normalize to lowercase
        password = payload.get('password', '').strip()

        # Generate ID
        last_agent = Agent.objects.order_by('-agent_id').first()
        if last_agent and last_agent.agent_id:
            match = re.search(r'AG-(\d+)$', last_agent.agent_id)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        new_id = f"AG-{next_num:04d}"

        agent = Agent(
            agent_id=new_id,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            role=role,
        )

        if password:
            agent.mot_de_passe = password  # Model's save() will hash it

        agent.save()

        return JsonResponse({
            'success': True,
            'agent': {
                'agent_id': agent.agent_id,
                'nom': agent.nom,
                'prenom': agent.prenom,
                'email': agent.email,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def edit_agent(request, agent_id):
    """Edit an existing agent."""
    agent = get_object_or_404(Agent, pk=agent_id)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        if 'nom' in payload:
            agent.nom = payload.get('nom', '').strip()
        if 'prenom' in payload:
            agent.prenom = payload.get('prenom', '').strip()
        if 'email' in payload:
            agent.email = payload.get('email', '').strip()
        if 'telephone' in payload:
            agent.telephone = payload.get('telephone', '').strip()
        if 'role' in payload:
            agent.role = payload.get('role', '').strip().lower()  # Normalize to lowercase
        if 'password' in payload and payload.get('password'):
            agent.mot_de_passe = payload.get('password')  # Model's save() will hash it

        agent.save()

        return JsonResponse({
            'success': True,
            'agent': {
                'agent_id': agent.agent_id,
                'nom': agent.nom,
                'prenom': agent.prenom,
                'email': agent.email,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_agent(request, agent_id):
    """Delete an agent."""
    agent = get_object_or_404(Agent, pk=agent_id)
    agent_id_str = agent.agent_id
    agent.delete()
    return JsonResponse({'success': True, 'deleted_id': agent_id_str})

def dashboard_clients(request):
    # Display clients list
    clients = Client.objects.all().order_by('-id_client')
    return render(request, 'DASHclients.html', {
        'clients': clients
    })


def add_client(request):
    if request.method != 'POST':
        return redirect('dashboard_clients')

    nom = request.POST.get('nom', '').strip()
    prenom = request.POST.get('prenom', '').strip()
    telephone = request.POST.get('telephone', '').strip()
    email = request.POST.get('email', '').strip()
    adresse = request.POST.get('adresse', '').strip()
    ville = request.POST.get('ville', '').strip()
    pays = request.POST.get('pays', '').strip()

    # Required fields
    if not (nom and prenom and email):
        return redirect('dashboard_clients')

    client = Client(
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        email=email,
        adresse=adresse,
        ville=ville,
        pays=pays
    )

    # Required by model
    client.generate_password()
    client.save()

    return redirect('dashboard_clients')


def show_client(request, client_id):
    """Return client data as JSON for the view modal."""
    client = get_object_or_404(Client, pk=client_id)
    data = {
        'id_client': client.id_client,
        'nom': client.nom,
        'prenom': client.prenom,
        'email': client.email,
        'telephone': client.telephone,
        'adresse': client.adresse,
        'ville': client.ville,
        'pays': client.pays,
        'date_inscription': client.date_inscription.isoformat()
    }
    return JsonResponse({'success': True, 'client': data})


@require_POST
def reset_client_password(request, client_id):
    """Generate a new password for the client, save it (hashed) and return the raw password once.

    Accessible to Django staff users OR to the project's session-based Agent admins
    (the app stores the role in request.session['role'] when an Agent logs in).
    Returns 403 if the caller isn't authorized.
    """
    # Allow if Django user is staff
    if not (request.user.is_authenticated and request.user.is_staff):
        # Fallback: allow if session indicates an Agent with role 'admin' or 'agent'
        if request.session.get('role', '').lower() not in ('admin', 'agent'):
            return JsonResponse({'success': False, 'error': 'forbidden'}, status=403)

    client = get_object_or_404(Client, pk=client_id)
    raw = client.generate_password()
    client.save()
    return JsonResponse({'success': True, 'password': raw})


@require_POST
def edit_client(request, client_id):
    """Edit an existing client. Accepts JSON or form-encoded POST.
    Returns JSON with updated values.
    """
    client = get_object_or_404(Client, pk=client_id)

    # parse JSON if sent
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON')
    else:
        payload = request.POST

    # Update allowed fields
    for field in ('nom', 'prenom', 'email', 'telephone', 'adresse', 'ville', 'pays'):
        if field in payload:
            setattr(client, field, payload.get(field))

    client.save()

    return JsonResponse({'success': True, 'client': {
        'id_client': client.id_client,
        'nom': client.nom,
        'prenom': client.prenom,
        'email': client.email,
        'telephone': client.telephone,
        'adresse': client.adresse,
        'ville': client.ville,
        'pays': client.pays,
        'date_inscription': client.date_inscription.isoformat()
    }})


@require_POST
def delete_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    client.delete()
    return JsonResponse({'success': True})


def dashboard_shipments(request):
    shipments = Shipment.objects.all().order_by('-date_creation')
    drivers = Chauffeur.objects.filter(disponibilite=True).order_by('nom')
    clients = Client.objects.all().order_by('nom')
    return render(request, 'DASHshipments.html', {
        'shipments': shipments,
        'drivers': drivers,
        'clients': clients,
    })


def list_shipments_json(request):
    """Return all shipments as JSON."""
    shipments = Shipment.objects.all().order_by('-date_creation')
    data = []
    for s in shipments:
        data.append({
            'id_shipment': s.id_shipment,
            'client': s.client.nom + ' ' + s.client.prenom if s.client else (s.package.client.nom + ' ' + s.package.client.prenom if s.package and s.package.client else ''),
            'client_id': s.client.id_client if s.client else (s.package.client.id_client if s.package and s.package.client else ''),
            'origin': s.origin,
            'destination': s.destination,
            'status': s.statut,
            'driver': s.driver.nom + ' ' + s.driver.prenom if s.driver else '',
            'driver_id': s.driver.id_chauffeur if s.driver else '',
            'date': s.shipment_date.isoformat() if s.shipment_date else '',
            'zone': s.zone,
            'speed': s.speed,
        })
    return JsonResponse({'success': True, 'shipments': data})


def show_shipment(request, shipment_id):
    """Return shipment data as JSON for the view modal."""
    shipment = get_object_or_404(Shipment, pk=shipment_id)
    data = {
        'id_shipment': shipment.id_shipment,
        'client': shipment.client.nom + ' ' + shipment.client.prenom if shipment.client else '',
        'client_id': shipment.client.id_client if shipment.client else '',
        'origin': shipment.origin,
        'destination': shipment.destination,
        'status': shipment.statut,
        'driver': shipment.driver.nom + ' ' + shipment.driver.prenom if shipment.driver else '',
        'driver_id': shipment.driver.id_chauffeur if shipment.driver else '',
        'date': shipment.shipment_date.isoformat() if shipment.shipment_date else '',
        'zone': shipment.zone,
        'speed': shipment.speed,
        'distance': str(shipment.distance) if shipment.distance else '',
        'description': shipment.description,
    }
    return JsonResponse({'success': True, 'shipment': data})


@require_POST
def add_shipment(request):
    """Create a new shipment."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        client_id = payload.get('client_id', '').strip()
        origin = payload.get('origin', '').strip()
        destination = payload.get('destination', '').strip()
        status = payload.get('status', 'PENDING').strip()
        driver_id = payload.get('driver_id', '').strip()
        shipment_date = payload.get('date', '').strip()
        zone = payload.get('zone', 'NATIONAL').strip()
        speed = payload.get('speed', 'NORMAL').strip()
        distance = payload.get('distance', '0').strip()

        # Get client
        client = None
        if client_id:
            try:
                client = Client.objects.get(pk=client_id)
            except Client.DoesNotExist:
                pass

        # Get driver
        driver = None
        if driver_id:
            try:
                driver = Chauffeur.objects.get(pk=driver_id)
            except Chauffeur.DoesNotExist:
                pass

        # Create a dummy package for the shipment (required by model)
        # Use a UUID-based tracking number to avoid UNIQUE constraint races
        def _gen_tracking():
            return f'TRK-{uuid.uuid4().hex[:12].upper()}'

        package = Package(
            client=client,
            weight=0,
            number_of_pieces=1,
            package_type='OTHER',
            tracking_number=_gen_tracking()
        )

        # Try to save and retry a few times if we hit a UNIQUE constraint
        for _ in range(5):
            try:
                package.save()
                break
            except IntegrityError:
                package.tracking_number = _gen_tracking()
        else:
            raise IntegrityError('Could not generate unique tracking_number after retries')

        shipment = Shipment(
            package=package,
            client=client,
            origin=origin,
            destination=destination,
            statut=status,
            driver=driver,
            zone=zone,
            speed=speed,
            distance=float(distance) if distance else 0,
        )

        if shipment_date:
            # Convert string date to date object if needed
            if isinstance(shipment_date, str):
                shipment.shipment_date = datetime.strptime(shipment_date, '%Y-%m-%d').date()
            else:
                shipment.shipment_date = shipment_date

        shipment.save()

        return JsonResponse({
            'success': True,
            'shipment': {
                'id_shipment': shipment.id_shipment,
                'client': client.nom + ' ' + client.prenom if client else '',
                'origin': shipment.origin,
                'destination': shipment.destination,
                'status': shipment.statut,
                'driver': driver.nom + ' ' + driver.prenom if driver else '',
                'date': shipment.shipment_date.isoformat() if shipment.shipment_date else '',
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def edit_shipment(request, shipment_id):
    """Edit an existing shipment."""
    shipment = get_object_or_404(Shipment, pk=shipment_id)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        if 'origin' in payload:
            shipment.origin = payload.get('origin', '').strip()
        if 'destination' in payload:
            shipment.destination = payload.get('destination', '').strip()
        if 'status' in payload:
            shipment.statut = payload.get('status', '').strip()
        if 'date' in payload and payload.get('date'):
            date_val = payload.get('date')
            # Convert string date to date object if needed
            if isinstance(date_val, str):
                shipment.shipment_date = datetime.strptime(date_val, '%Y-%m-%d').date()
            else:
                shipment.shipment_date = date_val
        if 'zone' in payload:
            shipment.zone = payload.get('zone', '').strip()
        if 'speed' in payload:
            shipment.speed = payload.get('speed', '').strip()

        # Update client
        client_id = payload.get('client_id', '').strip()
        if client_id:
            try:
                shipment.client = Client.objects.get(pk=client_id)
            except Client.DoesNotExist:
                pass

        # Update driver
        driver_id = payload.get('driver_id', '').strip()
        if driver_id:
            try:
                shipment.driver = Chauffeur.objects.get(pk=driver_id)
            except Chauffeur.DoesNotExist:
                shipment.driver = None
        elif 'driver_id' in payload:
            shipment.driver = None

        shipment.save()

        return JsonResponse({
            'success': True,
            'shipment': {
                'id_shipment': shipment.id_shipment,
                'client': shipment.client.nom + ' ' + shipment.client.prenom if shipment.client else '',
                'origin': shipment.origin,
                'destination': shipment.destination,
                'status': shipment.statut,
                'driver': shipment.driver.nom + ' ' + shipment.driver.prenom if shipment.driver else '',
                'date': shipment.shipment_date.isoformat() if shipment.shipment_date else '',
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_shipment(request, shipment_id):
    """Delete a shipment."""
    shipment = get_object_or_404(Shipment, pk=shipment_id)
    shipment_id_str = shipment.id_shipment
    # Also delete the associated package
    if shipment.package:
        shipment.package.delete()
    shipment.delete()
    return JsonResponse({'success': True, 'deleted_id': shipment_id_str})


def drivers(request):

    if request.method == "POST":
        action = request.POST.get("action")
        driver_id = request.POST.get("driver_id")

        # DELETE DRIVER
        if action == "delete" and driver_id:
            chauffeur = get_object_or_404(Chauffeur, id_chauffeur=driver_id)
            chauffeur.delete()
            return redirect('dashboard_drivers')

        # EDIT DRIVER
        if action == "edit" and driver_id:
            chauffeur = get_object_or_404(Chauffeur, id_chauffeur=driver_id)

            chauffeur.nom = request.POST.get("nom", chauffeur.nom)
            chauffeur.prenom = request.POST.get("prenom", chauffeur.prenom)
            chauffeur.email = request.POST.get("email", chauffeur.email)
            chauffeur.telephone = request.POST.get("telephone", chauffeur.telephone)
            chauffeur.numero_permis = request.POST.get("numero_permis", chauffeur.numero_permis)
            # Allow editing of statut
            chauffeur.statut = request.POST.get("statut", chauffeur.statut)
            # assign vehicle if provided (id_vehicule expected)
            veh_id = request.POST.get('vehicule')
            if veh_id:
                try:
                    veh = Vehicule.objects.get(id_vehicule=veh_id)
                    chauffeur.vehicule = veh
                except Vehicule.DoesNotExist:
                    chauffeur.vehicule = None

            chauffeur.save()
            return redirect('dashboard_drivers')

    # GET REQUEST
    chauffeurs = Chauffeur.objects.all().order_by('-id_chauffeur')
    vehicules = Vehicule.objects.all().order_by('-id_vehicule')
    return render(request, 'drivers.html', {
        'drivers': chauffeurs,
        'vehicles': vehicules,
    })


def show_driver(request, driver_id):
    """Return driver data as JSON for the view modal."""
    chauffeur = get_object_or_404(Chauffeur, pk=driver_id)
    data = {
        'id_chauffeur': chauffeur.id_chauffeur,
        'nom': chauffeur.nom,
        'prenom': chauffeur.prenom,
        'email': chauffeur.email,
        'telephone': chauffeur.telephone,
        'numero_permis': chauffeur.numero_permis,
        'disponibilite': chauffeur.disponibilite,
        'statut': chauffeur.statut,
        'vehicule': chauffeur.vehicule.immatriculation if chauffeur.vehicule else None,
        'vehicule_id': chauffeur.vehicule.id_vehicule if chauffeur.vehicule else None,
        'date_embauche': chauffeur.date_embauche.isoformat() if chauffeur.date_embauche else None,
    }
    return JsonResponse({'success': True, 'driver': data})


@require_POST
def add_driver_ajax(request):
    """Create a new driver via AJAX."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        nom = payload.get('nom', '').strip()
        prenom = payload.get('prenom', '').strip()
        email = payload.get('email', '').strip()
        telephone = payload.get('telephone', '').strip()
        numero_permis = payload.get('numero_permis', '').strip()
        vehicule_id = payload.get('vehicule_id', '').strip()
        statut = payload.get('statut', 'actif').strip()

        chauffeur = Chauffeur(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            numero_permis=numero_permis,
            statut=statut,
            disponibilite=True if statut == 'actif' else False,
        )

        if vehicule_id:
            try:
                veh = Vehicule.objects.get(id_vehicule=vehicule_id)
                chauffeur.vehicule = veh
            except Vehicule.DoesNotExist:
                pass

        chauffeur.generate_password_driver()

        return JsonResponse({
            'success': True,
            'driver': {
                'id_chauffeur': chauffeur.id_chauffeur,
                'nom': chauffeur.nom,
                'prenom': chauffeur.prenom,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def edit_driver_ajax(request, driver_id):
    """Edit an existing driver via AJAX."""
    chauffeur = get_object_or_404(Chauffeur, pk=driver_id)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        if 'nom' in payload:
            chauffeur.nom = payload.get('nom', '').strip()
        if 'prenom' in payload:
            chauffeur.prenom = payload.get('prenom', '').strip()
        if 'email' in payload:
            chauffeur.email = payload.get('email', '').strip()
        if 'telephone' in payload:
            chauffeur.telephone = payload.get('telephone', '').strip()
        if 'numero_permis' in payload:
            chauffeur.numero_permis = payload.get('numero_permis', '').strip()
        if 'statut' in payload:
            chauffeur.statut = payload.get('statut', '').strip()
            chauffeur.disponibilite = chauffeur.statut == 'actif'

        vehicule_id = payload.get('vehicule_id', '').strip()
        if vehicule_id:
            try:
                veh = Vehicule.objects.get(id_vehicule=vehicule_id)
                chauffeur.vehicule = veh
            except Vehicule.DoesNotExist:
                chauffeur.vehicule = None
        elif 'vehicule_id' in payload:
            chauffeur.vehicule = None

        chauffeur.save()

        return JsonResponse({
            'success': True,
            'driver': {
                'id_chauffeur': chauffeur.id_chauffeur,
                'nom': chauffeur.nom,
                'prenom': chauffeur.prenom,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_driver_ajax(request, driver_id):
    """Delete a driver via AJAX."""
    chauffeur = get_object_or_404(Chauffeur, pk=driver_id)
    driver_id_str = chauffeur.id_chauffeur
    chauffeur.delete()
    return JsonResponse({'success': True, 'deleted_id': driver_id_str})


@require_POST
def reset_driver_password(request, driver_id):
    """Generate a new password for the driver and return the raw password once.

    Accessible to Django staff users OR to the project's session-based Agent admins
    (the app stores the role in request.session['role'] when an Agent logs in).
    Returns 403 if the caller isn't authorized.
    """
    # Allow if Django user is staff
    if not (request.user.is_authenticated and request.user.is_staff):
        # Fallback: allow if session indicates an Agent with role 'admin' or 'agent'
        if request.session.get('role', '').lower() not in ('admin', 'agent'):
            return JsonResponse({'success': False, 'error': 'forbidden'}, status=403)

    chauffeur = get_object_or_404(Chauffeur, pk=driver_id)
    raw = chauffeur.generate_password_driver()
    return JsonResponse({'success': True, 'password': raw})

def add_driver(request):
    """Create a new Chauffeur from the dashboard Add Driver form."""
    if request.method != 'POST':
        return redirect('dashboard_drivers')

    nom = request.POST.get('nom', '').strip()
    prenom = request.POST.get('prenom', '').strip()
    telephone = request.POST.get('telephone', '').strip()
    email = request.POST.get('email', '').strip()
    numero_permis = request.POST.get('numero_permis', '').strip()
    disponibilite = request.POST.get('disponibilite', '1')
    statut = request.POST.get('statut', 'actif')
    veh_id = request.POST.get('vehicule')

    # Required basic fields
    if not (nom and prenom and email and numero_permis):
        return redirect('dashboard_drivers')

    # Map disponibilite to boolean
    disp_bool = str(disponibilite) in ('1', 'true', 'True', 'on')

    chauffeur = Chauffeur(
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        email=email,
        numero_permis=numero_permis,
        disponibilite=disp_bool,
        statut=statut
    )

    # assign vehicle if provided
    if veh_id:
        try:
            veh = Vehicule.objects.get(id_vehicule=veh_id)
            chauffeur.vehicule = veh
        except Vehicule.DoesNotExist:
            chauffeur.vehicule = None

    # generate and save password (generate_password_driver saves the instance)
    try:
        raw = chauffeur.generate_password_driver()
    except Exception:
        # on error (unique constraints etc) just redirect back for now
        return redirect('dashboard_drivers')

    return redirect('dashboard_drivers')


def vehicles(request):
    vehicles_list = Vehicule.objects.all().order_by('-id_vehicule')
    return render(request, 'vehicles.html', {
        'vehicles': vehicles_list,
    })


def show_vehicle(request, vehicle_id):
    """Return vehicle data as JSON for the view modal."""
    vehicle = get_object_or_404(Vehicule, pk=vehicle_id)
    # The Vehicule model stores different field names than older UI expects.
    # Provide backward-compatible keys where possible.
    # Attempt to split marque/modele from type_vehicule if encoded there.
    marque = ''
    modele = ''
    type_display = vehicle.type_vehicule or ''
    # If type_vehicule was stored as "<type> - <marque> <modele>" try to split
    if ' - ' in type_display:
        parts = type_display.split(' - ', 1)
        type_display = parts[0]
        rest = parts[1]
        # naive split for marque/modele
        tokens = rest.split(' ', 1)
        marque = tokens[0] if tokens else ''
        modele = tokens[1] if len(tokens) > 1 else ''

    data = {
        'id_vehicule': vehicle.id_vehicule,
        'immatriculation': vehicle.immatriculation,
        'marque': marque,
        'modele': modele,
        'type_vehicule': type_display,
        # Provide canonical keys expected by the frontend
        'capacite_charge': str(vehicle.capacite_charge) if vehicle.capacite_charge is not None else '',
        'consommation': str(vehicle.consommation) if getattr(vehicle, 'consommation', None) is not None else '',
        'date_mise_service': vehicle.date_mise_service.isoformat() if vehicle.date_mise_service else '',
        'etat': vehicle.etat,
    }
    return JsonResponse({'success': True, 'vehicle': data})


@require_POST
def add_vehicle(request):
    """Create a new vehicle."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        immatriculation = payload.get('immatriculation', '').strip()
        marque = payload.get('marque', '').strip()
        modele = payload.get('modele', '').strip()
        type_vehicule = payload.get('type_vehicule', 'camion').strip()
        # Accept either legacy 'capacite' or new 'capacite_charge'
        capacite = payload.get('capacite_charge', payload.get('capacite', '') )
        # Consumption key
        consommation = payload.get('consommation', '').strip()
        # Accept either full date or just year: 'date_mise_service' or legacy 'annee'
        date_mise_service_val = payload.get('date_mise_service', payload.get('annee', '') ).strip()
        statut = payload.get('etat', payload.get('statut', 'disponible')).strip()

        # Encode marque/modele into type_vehicule if provided to preserve info
        if marque or modele:
            combined = f"{marque} {modele}".strip()
            type_vehicule = f"{type_vehicule} - {combined}"

        # Check uniqueness of immatriculation before attempting to create
        if immatriculation:
            if Vehicule.objects.filter(immatriculation__iexact=immatriculation).exists():
                return JsonResponse({'success': False, 'error': 'immatriculation_exists', 'message': 'A vehicle with this immatriculation already exists.'}, status=400)

        # Parse date_mise_service if provided as a full date, otherwise use year if available
        dms = None
        if date_mise_service_val:
            try:
                # try full ISO date first
                dms = datetime.strptime(date_mise_service_val, '%Y-%m-%d').date()
            except Exception:
                try:
                    # fallback: treat as year
                    dms = date(int(date_mise_service_val), 1, 1)
                except Exception:
                    dms = None

        vehicle = Vehicule(
            immatriculation=immatriculation,
            type_vehicule=type_vehicule,
            capacite_charge=float(capacite) if capacite else None,
            consommation=float(consommation) if consommation else None,
            date_mise_service=dms,
            etat=statut,
        )
        try:
            vehicle.save()
        except IntegrityError as e:
            # Fallback: possible race or unique constraint violation
            return JsonResponse({'success': False, 'error': 'integrity_error', 'message': str(e)}, status=400)

        return JsonResponse({
            'success': True,
            'vehicle': {
                'id_vehicule': vehicle.id_vehicule,
                'immatriculation': vehicle.immatriculation,
                # Provide backward-compatible keys by extracting from type_vehicule
                'marque': _extract_marque_modele_from_type(vehicle.type_vehicule)[0],
                'modele': _extract_marque_modele_from_type(vehicle.type_vehicule)[1],
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def edit_vehicle(request, vehicle_id):
    """Edit an existing vehicle."""
    vehicle = get_object_or_404(Vehicule, pk=vehicle_id)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        if 'immatriculation' in payload:
            new_immat = payload.get('immatriculation', '').strip()
            # If changing immatriculation, ensure uniqueness (ignore current vehicle)
            if new_immat and new_immat.lower() != (vehicle.immatriculation or '').lower():
                if Vehicule.objects.filter(immatriculation__iexact=new_immat).exclude(pk=vehicle.pk).exists():
                    return JsonResponse({'success': False, 'error': 'immatriculation_exists', 'message': 'Another vehicle already uses this immatriculation.'}, status=400)
            vehicle.immatriculation = new_immat
        # Map incoming (possibly old) keys to current model fields
        if 'marque' in payload or 'modele' in payload:
            marque = payload.get('marque', '').strip()
            modele = payload.get('modele', '').strip()
            # append or replace marque/modele encoding in type_vehicule
            base_type = vehicle.type_vehicule.split(' - ')[0] if vehicle.type_vehicule else ''
            combined = f"{marque} {modele}".strip()
            vehicle.type_vehicule = f"{base_type} - {combined}" if combined else base_type
        if 'type_vehicule' in payload:
            vehicle.type_vehicule = payload.get('type_vehicule', '').strip()
        # Accept both 'capacite' and 'capacite_charge'
        if 'capacite' in payload or 'capacite_charge' in payload:
            try:
                vehicle.capacite_charge = float(payload.get('capacite_charge', payload.get('capacite', 0)))
            except Exception:
                vehicle.capacite_charge = None
        if 'consommation' in payload:
            try:
                vehicle.consommation = float(payload.get('consommation', 0))
            except Exception:
                vehicle.consommation = None
        # Accept full date string 'date_mise_service' or legacy 'annee'
        if 'date_mise_service' in payload and payload.get('date_mise_service'):
            try:
                vehicle.date_mise_service = datetime.strptime(payload.get('date_mise_service'), '%Y-%m-%d').date()
            except Exception:
                vehicle.date_mise_service = None
        elif 'annee' in payload and payload.get('annee'):
            try:
                vehicle.date_mise_service = date(int(payload.get('annee')), 1, 1)
            except Exception:
                vehicle.date_mise_service = None
        if 'etat' in payload or 'statut' in payload:
            vehicle.etat = payload.get('etat', payload.get('statut', '')).strip()

        try:
            vehicle.save()
        except IntegrityError as e:
            return JsonResponse({'success': False, 'error': 'integrity_error', 'message': str(e)}, status=400)

        return JsonResponse({
            'success': True,
            'vehicle': {
                'id_vehicule': vehicle.id_vehicule,
                'immatriculation': vehicle.immatriculation,
                'marque': _extract_marque_modele_from_type(vehicle.type_vehicule)[0],
                'modele': _extract_marque_modele_from_type(vehicle.type_vehicule)[1],
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_vehicle(request, vehicle_id):
    """Delete a vehicle."""
    vehicle = get_object_or_404(Vehicule, pk=vehicle_id)
    vehicle_id_str = vehicle.id_vehicule
    vehicle.delete()
    return JsonResponse({'success': True, 'deleted_id': vehicle_id_str})


def incidents(request):
    incidents_list = Incident.objects.all().order_by('-incident_date')
    return render(request, 'incidents.html', {
        'incidents': incidents_list,
    })


def list_incidents_json(request):
    """Return all incidents as JSON."""
    incidents_list = Incident.objects.all().order_by('-incident_date')
    data = []
    for inc in incidents_list:
        data.append({
            'id_incident': inc.id_incident,
            'incident_type': inc.incident_type,
            'type_display': inc.get_incident_type_display(),
            'description': inc.description,
            'status': inc.status,
            'status_display': inc.get_status_display(),
            'priority': inc.priority,
            'priority_display': inc.get_priority_display(),
            'date': inc.incident_date.strftime('%Y-%m-%d') if inc.incident_date else '',
            'commentaire': inc.commentaire,
        })
    return JsonResponse({'success': True, 'incidents': data})


def show_incident(request, incident_id):
    """Return incident data as JSON for the view modal."""
    incident = get_object_or_404(Incident, pk=incident_id)
    data = {
        'id_incident': incident.id_incident,
        'incident_type': incident.incident_type,
        'type_display': incident.get_incident_type_display(),
        'description': incident.description,
        'status': incident.status,
        'status_display': incident.get_status_display(),
        'priority': incident.priority,
        'priority_display': incident.get_priority_display(),
        'date': incident.incident_date.strftime('%Y-%m-%d') if incident.incident_date else '',
        'commentaire': incident.commentaire,
        'created_at': incident.created_at.isoformat() if incident.created_at else '',
        'resolution_date': incident.resolution_date.isoformat() if incident.resolution_date else '',
    }
    return JsonResponse({'success': True, 'incident': data})


@require_POST
def add_incident(request):
    """Create a new incident."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        incident_type = payload.get('incident_type', 'other').strip()
        description = payload.get('description', '').strip()
        status = payload.get('status', 'new').strip()
        priority = payload.get('priority', 'medium').strip()
        incident_date = payload.get('date', '').strip()
        commentaire = payload.get('commentaire', '').strip()

        incident = Incident(
            incident_type=incident_type,
            description=description,
            status=status,
            priority=priority,
            commentaire=commentaire,
        )

        if incident_date:
            from django.utils import timezone
            from datetime import datetime
            incident.incident_date = timezone.make_aware(datetime.strptime(incident_date, '%Y-%m-%d'))

        incident.save()

        return JsonResponse({
            'success': True,
            'incident': {
                'id_incident': incident.id_incident,
                'incident_type': incident.incident_type,
                'type_display': incident.get_incident_type_display(),
                'description': incident.description,
                'status': incident.status,
                'status_display': incident.get_status_display(),
                'priority': incident.priority,
                'date': incident.incident_date.strftime('%Y-%m-%d') if incident.incident_date else '',
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def edit_incident(request, incident_id):
    """Edit an existing incident."""
    incident = get_object_or_404(Incident, pk=incident_id)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        if 'incident_type' in payload:
            incident.incident_type = payload.get('incident_type', '').strip()
        if 'description' in payload:
            incident.description = payload.get('description', '').strip()
        if 'status' in payload:
            incident.status = payload.get('status', '').strip()
        if 'priority' in payload:
            incident.priority = payload.get('priority', '').strip()
        if 'commentaire' in payload:
            incident.commentaire = payload.get('commentaire', '').strip()
        if 'date' in payload and payload.get('date'):
            from django.utils import timezone
            from datetime import datetime
            incident.incident_date = timezone.make_aware(datetime.strptime(payload.get('date'), '%Y-%m-%d'))

        incident.save()

        return JsonResponse({
            'success': True,
            'incident': {
                'id_incident': incident.id_incident,
                'incident_type': incident.incident_type,
                'type_display': incident.get_incident_type_display(),
                'description': incident.description,
                'status': incident.status,
                'status_display': incident.get_status_display(),
                'priority': incident.priority,
                'date': incident.incident_date.strftime('%Y-%m-%d') if incident.incident_date else '',
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_incident(request, incident_id):
    """Delete an incident."""
    incident = get_object_or_404(Incident, pk=incident_id)
    incident_id_str = incident.id_incident
    incident.delete()
    return JsonResponse({'success': True, 'deleted_id': incident_id_str})


def invoices(request):
    invoices_list = Invoice.objects.all().order_by('-invoice_date')
    clients = Client.objects.all().order_by('nom')
    shipments = Shipment.objects.all().order_by('-date_creation')
    return render(request, 'invoices.html', {
        'invoices': invoices_list,
        'clients': clients,
        'shipments': shipments,
    })


def show_invoice(request, invoice_id):
    """Return invoice data as JSON for the view modal."""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    data = {
        'id_invoice': invoice.id_invoice,
        'client': f"{invoice.client.nom} {invoice.client.prenom}" if invoice.client else '',
        'client_id': invoice.client.id_client if invoice.client else '',
        'shipment': invoice.shipment.id_shipment if invoice.shipment else '',
        'shipment_id': invoice.shipment.id_shipment if invoice.shipment else '',
        'total_amount': str(invoice.total_amount),
        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else '',
    }
    return JsonResponse({'success': True, 'invoice': data})


@require_POST
def add_invoice(request):
    """Create a new invoice."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        client_id = payload.get('client_id', '').strip()
        shipment_id = payload.get('shipment_id', '').strip()
        total_amount = payload.get('total_amount', '0').strip()
        invoice_date = payload.get('invoice_date', '').strip()

        client = None
        if client_id:
            client = Client.objects.get(pk=client_id)

        shipment = None
        if shipment_id:
            shipment = Shipment.objects.get(pk=shipment_id)

        invoice = Invoice(
            client=client,
            shipment=shipment,
            total_amount=float(total_amount) if total_amount else 0,
        )

        if invoice_date:
            invoice.invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()

        invoice.save()

        return JsonResponse({
            'success': True,
            'invoice': {
                'id_invoice': invoice.id_invoice,
                'client': f"{client.nom} {client.prenom}" if client else '',
                'total_amount': str(invoice.total_amount),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_invoice(request, invoice_id):
    """Delete an invoice."""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice_id_str = invoice.id_invoice
    invoice.delete()
    return JsonResponse({'success': True, 'deleted_id': invoice_id_str})


def package(request):
    packages_list = Package.objects.all().order_by('-id_package')
    clients = Client.objects.all().order_by('nom')
    return render(request, 'package.html', {
        'packages': packages_list,
        'clients': clients,
    })


def show_package(request, package_id):
    """Return package data as JSON for the view modal."""
    package = get_object_or_404(Package, pk=package_id)
    data = {
        'id_package': package.id_package,
        'tracking_number': package.tracking_number,
        'client': f"{package.client.nom} {package.client.prenom}" if package.client else '',
        'client_id': package.client.id_client if package.client else '',
        'weight': str(package.weight),
        'number_of_pieces': package.number_of_pieces,
        'package_type': package.package_type,
        'package_type_display': package.get_package_type_display(),
        'date_creation': package.date_creation.strftime('%Y-%m-%d %H:%M') if package.date_creation else '',
    }
    return JsonResponse({'success': True, 'package': data})


@require_POST
def add_package(request):
    """Create a new package."""
    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        client_id = payload.get('client_id', '').strip()
        weight = payload.get('weight', '0').strip()
        number_of_pieces = payload.get('number_of_pieces', '1').strip()
        package_type = payload.get('package_type', 'OTHER').strip()

        client = None
        if client_id:
            client = Client.objects.get(pk=client_id)

        # Generate a safe unique tracking number
        def _gen_tracking():
            return f'TRK-{uuid.uuid4().hex[:12].upper()}'

        package = Package(
            client=client,
            weight=float(weight) if weight else 0,
            number_of_pieces=int(number_of_pieces) if number_of_pieces else 1,
            package_type=package_type,
            tracking_number=_gen_tracking()
        )

        for _ in range(5):
            try:
                package.save()
                break
            except IntegrityError:
                package.tracking_number = _gen_tracking()
        else:
            raise IntegrityError('Could not generate unique tracking_number after retries')

        return JsonResponse({
            'success': True,
            'package': {
                'id_package': package.id_package,
                'tracking_number': package.tracking_number,
                'weight': str(package.weight),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def edit_package(request, package_id):
    """Edit an existing package."""
    package = get_object_or_404(Package, pk=package_id)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
        else:
            payload = request.POST

        if 'client_id' in payload and payload.get('client_id'):
            try:
                package.client = Client.objects.get(pk=payload.get('client_id'))
            except Client.DoesNotExist:
                pass
        if 'weight' in payload:
            package.weight = float(payload.get('weight', 0))
        if 'number_of_pieces' in payload:
            package.number_of_pieces = int(payload.get('number_of_pieces', 1))
        if 'package_type' in payload:
            package.package_type = payload.get('package_type', '').strip()

        package.save()

        return JsonResponse({
            'success': True,
            'package': {
                'id_package': package.id_package,
                'tracking_number': package.tracking_number,
                'weight': str(package.weight),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_package(request, package_id):
    """Delete a package."""
    package = get_object_or_404(Package, pk=package_id)
    package_id_str = package.id_package
    package.delete()
    return JsonResponse({'success': True, 'deleted_id': package_id_str})
