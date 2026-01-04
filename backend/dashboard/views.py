from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
import json
from django.contrib.admin.views.decorators import staff_member_required

from database.models import Client, Chauffeur


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

            chauffeur.save()
            return redirect('dashboard_drivers')

    # GET REQUEST
    chauffeurs = Chauffeur.objects.all().order_by('-id_chauffeur')
    return render(request, 'drivers.html', {
        'drivers': chauffeurs
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
        'date_embauche': chauffeur.date_embauche.isoformat() if chauffeur.date_embauche else None,
    }
    return JsonResponse({'success': True, 'driver': data})


@staff_member_required
@require_POST
@require_POST
@staff_member_required
def reset_driver_password(request, driver_id):
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

    # generate and save password (generate_password_driver saves the instance)
    try:
        raw = chauffeur.generate_password_driver()
    except Exception:
        # on error (unique constraints etc) just redirect back for now
        return redirect('dashboard_drivers')

    return redirect('dashboard_drivers')


def vehicles(request):
    return render(request, 'vehicles.html')


def incidents(request):
    return render(request, 'incidents.html')


def invoices(request):
    return render(request, 'invoices.html')


def package(request):
    return render(request, 'package.html')
