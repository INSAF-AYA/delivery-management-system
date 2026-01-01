from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
import json
from django.contrib.admin.views.decorators import staff_member_required

from database.models import Client


def index(request):
    return render(request, 'DASHindex.html')


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
@staff_member_required
def reset_client_password(request, client_id):
    """Generate a new password for the client, save it (hashed) and return the raw password once.

    This endpoint is protected to staff members only.
    """
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
    return render(request, 'DASHshipments.html')


def drivers(request):
    return render(request, 'drivers.html')


def vehicles(request):
    return render(request, 'vehicles.html')


def incidents(request):
    return render(request, 'incidents.html')


def invoices(request):
    return render(request, 'invoices.html')


def package(request):
    return render(request, 'package.html')
