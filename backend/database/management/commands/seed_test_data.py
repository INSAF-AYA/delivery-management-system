from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import random

from database.models import (
    Client, Chauffeur, Vehicule, Service, Package, 
    Shipment, Incident, Reclamation, Agent, Tour
)


class Command(BaseCommand):
    help = 'Seed comprehensive test data into all database tables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Seeding comprehensive test data...'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # ========================
        # CLIENTS
        # ========================
        self.stdout.write('\n📦 Creating Clients...')
        clients_data = [
            {'nom': 'Dupont', 'prenom': 'Jean', 'email': 'jean.dupont@email.com', 'telephone': '+33612345678', 'adresse': '15 Rue de Paris', 'ville': 'Paris', 'pays': 'France'},
            {'nom': 'Martin', 'prenom': 'Marie', 'email': 'marie.martin@email.com', 'telephone': '+33623456789', 'adresse': '22 Avenue des Champs', 'ville': 'Lyon', 'pays': 'France'},
            {'nom': 'Bernard', 'prenom': 'Pierre', 'email': 'pierre.bernard@email.com', 'telephone': '+33634567890', 'adresse': '8 Boulevard Victor Hugo', 'ville': 'Marseille', 'pays': 'France'},
            {'nom': 'Petit', 'prenom': 'Sophie', 'email': 'sophie.petit@email.com', 'telephone': '+33645678901', 'adresse': '45 Rue Gambetta', 'ville': 'Toulouse', 'pays': 'France'},
            {'nom': 'Robert', 'prenom': 'Luc', 'email': 'luc.robert@email.com', 'telephone': '+33656789012', 'adresse': '33 Place de la République', 'ville': 'Bordeaux', 'pays': 'France'},
            {'nom': 'Moreau', 'prenom': 'Emma', 'email': 'emma.moreau@email.com', 'telephone': '+33667890123', 'adresse': '12 Rue du Commerce', 'ville': 'Nantes', 'pays': 'France'},
        ]
        
        clients = []
        for data in clients_data:
            client, created = Client.objects.get_or_create(
                email=data['email'],
                defaults={**data, 'password_client': make_password('client123')}
            )
            clients.append(client)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {client.nom} {client.prenom} ({client.id_client})')

        # ========================
        # VEHICLES
        # ========================
        self.stdout.write('\n🚚 Creating Vehicles...')
        vehicles_data = [
            {'immatriculation': 'AB-123-CD', 'type_vehicule': 'Van', 'capacite_charge': 1500, 'consommation': 8.5, 'etat': 'disponible'},
            {'immatriculation': 'EF-456-GH', 'type_vehicule': 'Truck', 'capacite_charge': 5000, 'consommation': 15.0, 'etat': 'disponible'},
            {'immatriculation': 'IJ-789-KL', 'type_vehicule': 'Van', 'capacite_charge': 1200, 'consommation': 7.8, 'etat': 'en_maintenance'},
            {'immatriculation': 'MN-012-OP', 'type_vehicule': 'Motorcycle', 'capacite_charge': 50, 'consommation': 3.5, 'etat': 'disponible'},
            {'immatriculation': 'QR-345-ST', 'type_vehicule': 'Truck', 'capacite_charge': 8000, 'consommation': 18.0, 'etat': 'disponible'},
            {'immatriculation': 'UV-678-WX', 'type_vehicule': 'Van', 'capacite_charge': 2000, 'consommation': 9.2, 'etat': 'hors_service'},
        ]
        
        vehicles = []
        for data in vehicles_data:
            vehicle, created = Vehicule.objects.get_or_create(
                immatriculation=data['immatriculation'],
                defaults={**data, 'date_mise_service': timezone.now().date() - timedelta(days=random.randint(30, 365))}
            )
            vehicles.append(vehicle)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {vehicle.immatriculation} - {vehicle.type_vehicule} ({vehicle.id_vehicule})')

        # ========================
        # DRIVERS (CHAUFFEURS)
        # ========================
        self.stdout.write('\n🚗 Creating Drivers...')
        drivers_data = [
            {'nom': 'Lefevre', 'prenom': 'Antoine', 'email': 'antoine.lefevre@swiftship.com', 'telephone': '+33611111111', 'numero_permis': 'PERM001234', 'statut': 'actif'},
            {'nom': 'Girard', 'prenom': 'Thomas', 'email': 'thomas.girard@swiftship.com', 'telephone': '+33622222222', 'numero_permis': 'PERM002345', 'statut': 'actif'},
            {'nom': 'Bonnet', 'prenom': 'Claire', 'email': 'claire.bonnet@swiftship.com', 'telephone': '+33633333333', 'numero_permis': 'PERM003456', 'statut': 'actif'},
            {'nom': 'Dubois', 'prenom': 'Marc', 'email': 'marc.dubois@swiftship.com', 'telephone': '+33644444444', 'numero_permis': 'PERM004567', 'statut': 'en_conge'},
            {'nom': 'Roux', 'prenom': 'Julie', 'email': 'julie.roux@swiftship.com', 'telephone': '+33655555555', 'numero_permis': 'PERM005678', 'statut': 'actif'},
        ]
        
        drivers = []
        for i, data in enumerate(drivers_data):
            driver, created = Chauffeur.objects.get_or_create(
                email=data['email'],
                defaults={
                    **data, 
                    'password_driver': make_password('driver123'),
                    'vehicule': vehicles[i] if i < len(vehicles) else None
                }
            )
            drivers.append(driver)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {driver.nom} {driver.prenom} ({driver.id_chauffeur})')

        # ========================
        # SERVICES
        # ========================
        self.stdout.write('\n📋 Creating Services...')
        services_data = [
            {'speed': 'NORMAL', 'zone': 'NATIONAL'},
            {'speed': 'EXPRESS', 'zone': 'NATIONAL'},
            {'speed': 'NORMAL', 'zone': 'INTERNATIONAL'},
            {'speed': 'EXPRESS', 'zone': 'INTERNATIONAL'},
        ]
        
        services = []
        for data in services_data:
            service, created = Service.objects.get_or_create(**data)
            services.append(service)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {service.speed} - {service.zone}')

        # ========================
        # AGENTS
        # ========================
        self.stdout.write('\n👤 Creating Agents...')
        agents_data = [
            {'nom': 'Admin', 'prenom': 'System', 'email': 'admin@swiftship.com', 'role': 'admin', 'telephone': '+33600000001'},
            {'nom': 'Lambert', 'prenom': 'Paul', 'email': 'paul.lambert@swiftship.com', 'role': 'agent', 'telephone': '+33600000002'},
            {'nom': 'Fournier', 'prenom': 'Isabelle', 'email': 'isabelle.fournier@swiftship.com', 'role': 'agent', 'telephone': '+33600000003'},
        ]
        
        agents = []
        for data in agents_data:
            try:
                agent = Agent.objects.get(email=data['email'])
                agents.append(agent)
                self.stdout.write(f'  Exists: {agent.nom} {agent.prenom} ({agent.agent_id}) - {agent.role}')
            except Agent.DoesNotExist:
                agent = Agent.objects.create(
                    **data,
                    mot_de_passe='agent123',
                    date_embauche=timezone.now().date() - timedelta(days=random.randint(30, 500))
                )
                agents.append(agent)
                self.stdout.write(f'  Created: {agent.nom} {agent.prenom} ({agent.agent_id}) - {agent.role}')

        # ========================
        # PACKAGES
        # ========================
        self.stdout.write('\n📦 Creating Packages...')
        packages_data = [
            {'tracking_number': 'SW2026001234', 'client': clients[0], 'weight': 2.5, 'number_of_pieces': 1, 'package_type': 'DOC'},
            {'tracking_number': 'SW2026001235', 'client': clients[1], 'weight': 15.0, 'number_of_pieces': 2, 'package_type': 'ELEC'},
            {'tracking_number': 'SW2026001236', 'client': clients[2], 'weight': 50.0, 'number_of_pieces': 1, 'package_type': 'FURN'},
            {'tracking_number': 'SW2026001237', 'client': clients[3], 'weight': 0.5, 'number_of_pieces': 3, 'package_type': 'DOC'},
            {'tracking_number': 'SW2026001238', 'client': clients[4], 'weight': 8.0, 'number_of_pieces': 1, 'package_type': 'ELEC'},
            {'tracking_number': 'SW2026001239', 'client': clients[5], 'weight': 25.0, 'number_of_pieces': 4, 'package_type': 'OTHER'},
            {'tracking_number': 'SW2026001240', 'client': clients[0], 'weight': 3.2, 'number_of_pieces': 1, 'package_type': 'DOC'},
            {'tracking_number': 'SW2026001241', 'client': clients[1], 'weight': 12.5, 'number_of_pieces': 2, 'package_type': 'ELEC'},
        ]
        
        packages = []
        for data in packages_data:
            pkg, created = Package.objects.get_or_create(
                tracking_number=data['tracking_number'],
                defaults=data
            )
            packages.append(pkg)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {pkg.tracking_number} ({pkg.id_package})')

        # ========================
        # SHIPMENTS
        # ========================
        self.stdout.write('\n🚚 Creating Shipments...')
        shipments_data = [
            {'package': packages[0], 'client': clients[0], 'origin': 'Paris', 'destination': 'Lyon', 'zone': 'NATIONAL', 'speed': 'EXPRESS', 'distance': 465, 'statut': 'DELIVERED', 'driver': drivers[0]},
            {'package': packages[1], 'client': clients[1], 'origin': 'Lyon', 'destination': 'Marseille', 'zone': 'NATIONAL', 'speed': 'NORMAL', 'distance': 315, 'statut': 'IN_TRANSIT', 'driver': drivers[1]},
            {'package': packages[2], 'client': clients[2], 'origin': 'Marseille', 'destination': 'Toulouse', 'zone': 'NATIONAL', 'speed': 'NORMAL', 'distance': 405, 'statut': 'PENDING', 'driver': None},
            {'package': packages[3], 'client': clients[3], 'origin': 'Paris', 'destination': 'Brussels', 'zone': 'INTERNATIONAL', 'speed': 'EXPRESS', 'distance': 320, 'statut': 'IN_TRANSIT', 'driver': drivers[2]},
            {'package': packages[4], 'client': clients[4], 'origin': 'Bordeaux', 'destination': 'Nantes', 'zone': 'NATIONAL', 'speed': 'NORMAL', 'distance': 340, 'statut': 'DELIVERED', 'driver': drivers[0]},
            {'package': packages[5], 'client': clients[5], 'origin': 'Nantes', 'destination': 'Paris', 'zone': 'NATIONAL', 'speed': 'EXPRESS', 'distance': 385, 'statut': 'PENDING', 'driver': None},
            {'package': packages[6], 'client': clients[0], 'origin': 'Paris', 'destination': 'Madrid', 'zone': 'INTERNATIONAL', 'speed': 'NORMAL', 'distance': 1270, 'statut': 'IN_TRANSIT', 'driver': drivers[4]},
            {'package': packages[7], 'client': clients[1], 'origin': 'Lyon', 'destination': 'Geneva', 'zone': 'INTERNATIONAL', 'speed': 'EXPRESS', 'distance': 150, 'statut': 'DELIVERED', 'driver': drivers[1]},
        ]
        
        shipments = []
        for data in shipments_data:
            try:
                shipment = data['package'].shipment
                # Update existing
                for key, value in data.items():
                    if key != 'package':
                        setattr(shipment, key, value)
                shipment.shipment_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
                shipment.save()
                shipments.append(shipment)
                self.stdout.write(f'  Updated: {shipment.id_shipment} - {data["origin"]} → {data["destination"]}')
            except Shipment.DoesNotExist:
                shipment = Shipment.objects.create(
                    **data,
                    shipment_date=timezone.now().date() - timedelta(days=random.randint(1, 30))
                )
                shipments.append(shipment)
                self.stdout.write(f'  Created: {shipment.id_shipment} - {data["origin"]} → {data["destination"]}')

        # ========================
        # INCIDENTS
        # ========================
        self.stdout.write('\n⚠️ Creating Incidents...')
        incidents_data = [
            {'incident_type': 'delay', 'description': 'Traffic jam on highway A6 caused 2-hour delay', 'status': 'resolved', 'priority': 'medium'},
            {'incident_type': 'damage', 'description': 'Package corner damaged during loading', 'status': 'in_progress', 'priority': 'high'},
            {'incident_type': 'loss', 'description': 'Package misplaced at sorting center', 'status': 'open', 'priority': 'critical'},
            {'incident_type': 'technical', 'description': 'GPS tracker malfunction on vehicle VH000002', 'status': 'new', 'priority': 'low'},
            {'incident_type': 'accident', 'description': 'Minor collision in parking lot, no injuries', 'status': 'in_progress', 'priority': 'high'},
            {'incident_type': 'delay', 'description': 'Weather conditions delayed delivery by 1 day', 'status': 'closed', 'priority': 'low'},
            {'incident_type': 'other', 'description': 'Customer not available for delivery, rescheduled', 'status': 'resolved', 'priority': 'medium'},
        ]
        
        incidents = []
        for data in incidents_data:
            incident = Incident.objects.create(
                **data,
                incident_date=timezone.now() - timedelta(days=random.randint(1, 20)),
                commentaire=f"Initial report: {data['description'][:50]}..."
            )
            incidents.append(incident)
            self.stdout.write(f'  Created: {incident.id_incident} - {incident.incident_type} ({incident.status})')

        # ========================
        # RECLAMATIONS
        # ========================
        self.stdout.write('\n📝 Creating Reclamations...')
        reclamations_data = [
            {'nature': 'Late Delivery', 'description': 'Package arrived 3 days after expected date', 'status': 'resolved'},
            {'nature': 'Damaged Package', 'description': 'Contents were broken upon arrival', 'status': 'in_progress'},
            {'nature': 'Wrong Address', 'description': 'Delivered to neighbor instead of correct address', 'status': 'open'},
            {'nature': 'Missing Items', 'description': 'One item from the order was missing', 'status': 'new'},
            {'nature': 'Poor Service', 'description': 'Driver was rude during delivery', 'status': 'pending_customer'},
        ]
        
        reclamations = []
        for data in reclamations_data:
            reclamation = Reclamation.objects.create(
                **data,
                date_reclamation=timezone.now() - timedelta(days=random.randint(1, 15)),
                commentaire=f"Customer complaint registered"
            )
            reclamations.append(reclamation)
            self.stdout.write(f'  Created: {reclamation.id_reclamation} - {reclamation.nature} ({reclamation.status})')

        # ========================
        # TOURS
        # ========================
        self.stdout.write('\n🗺️ Creating Tours...')
        tours_data = [
            {'chauffeur': drivers[0], 'status': 'COMPLETED'},
            {'chauffeur': drivers[1], 'status': 'PENDING'},
            {'chauffeur': drivers[2], 'status': 'PENDING'},
        ]
        
        tours = []
        for i, data in enumerate(tours_data):
            tour = Tour.objects.create(
                **data,
                tour_date=timezone.now().date() - timedelta(days=i)
            )
            # Assign some shipments to tours
            if i < len(shipments):
                tour.shipments.add(shipments[i])
                if i + 1 < len(shipments):
                    tour.shipments.add(shipments[i + 1])
            tours.append(tour)
            self.stdout.write(f'  Created: {tour.id_tour} - Driver: {tour.chauffeur.nom} ({tour.status})')

        # ========================
        # SUMMARY
        # ========================
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ SEEDING COMPLETE!'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Clients: {Client.objects.count()}')
        self.stdout.write(f'  • Vehicles: {Vehicule.objects.count()}')
        self.stdout.write(f'  • Drivers: {Chauffeur.objects.count()}')
        self.stdout.write(f'  • Services: {Service.objects.count()}')
        self.stdout.write(f'  • Agents: {Agent.objects.count()}')
        self.stdout.write(f'  • Packages: {Package.objects.count()}')
        self.stdout.write(f'  • Shipments: {Shipment.objects.count()}')
        self.stdout.write(f'  • Incidents: {Incident.objects.count()}')
        self.stdout.write(f'  • Reclamations: {Reclamation.objects.count()}')
        self.stdout.write(f'  • Tours: {Tour.objects.count()}')
        
        self.stdout.write(self.style.WARNING('\n🔐 Default Passwords:'))
        self.stdout.write('  • Clients: client123')
        self.stdout.write('  • Drivers: driver123')
        self.stdout.write('  • Agents: agent123')
        self.stdout.write('  • Admin: admin@swiftship.com / agent123')
