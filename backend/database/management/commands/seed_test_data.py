from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from database.models import Client, Chauffeur, Package, Shipment


class Command(BaseCommand):
    help = 'Seed minimal test data (client, driver, package, shipment, expedition) into the database app'

    def handle(self, *args, **options):
        self.stdout.write('Seeding test data into database app...')

        # Create or get client
        client_email = 'testclient@example.com'
        client_password = 'clientpass123'
        client, created = Client.objects.get_or_create(
            email=client_email,
            defaults={
                'nom': 'Test',
                'prenom': 'Client',
                'telephone': '+33123456789',
                'adresse': '1 Rue Test',
                'ville': 'Testville',
                'pays': 'Testland'
            }
        )
        if created:
            client.password_client = make_password(client_password)
            client.save()
            self.stdout.write(f'Created Client {client.email} (id: {client.id_client})')
        else:
            self.stdout.write(f'Client already exists: {client.email} (id: {client.id_client})')

        # Create or get driver (chauffeur)
        driver_email = 'testdriver@example.com'
        driver_password = 'driverpass123'
        driver, dcreated = Chauffeur.objects.get_or_create(
            email=driver_email,
            defaults={
                'nom': 'Test',
                'prenom': 'Driver',
                'telephone': '+33987654321',
                'numero_permis': 'PERM123456'
            }
        )
        if dcreated:
            driver.password_driver = make_password(driver_password)
            driver.save()
            self.stdout.write(f'Created Driver {driver.email} (id: {driver.id_chauffeur})')
        else:
            self.stdout.write(f'Driver already exists: {driver.email} (id: {driver.id_chauffeur})')

        # Create a package
        tracking_number = 'SWTEST12345'
        pkg, pcreated = Package.objects.get_or_create(
            tracking_number=tracking_number,
            defaults={
                'client': client,
                'weight': 1.5,
                'number_of_pieces': 1,
                'package_type': 'OTHER'
            }
        )
        if pcreated:
            pkg.save()
            self.stdout.write(f'Created Package tracking={pkg.tracking_number} (id: {pkg.id_package})')
        else:
            self.stdout.write(f'Package already exists: {pkg.tracking_number} (id: {pkg.id_package})')

        # Create shipment if not exists
        try:
            shipment = pkg.shipment
            self.stdout.write(f'Existing Shipment found for package: {shipment.id_shipment}')
        except Shipment.DoesNotExist:
            shipment = Shipment.objects.create(
                package=pkg,
                zone='NATIONAL',
                speed='NORMAL',
                distance=12.5,
                shipment_date=timezone.now().date()
            )
            self.stdout.write(f'Created Shipment {shipment.id_shipment} for package {pkg.tracking_number}')

        # Attach expedition-like details onto the Shipment (we migrated
        # Expedition -> Shipment). If shipment already exists for this
        # package, update its driver/origin/destination/kilometrage.
        try:
            shipment = pkg.shipment
        except Shipment.DoesNotExist:
            shipment = None

        if shipment:
            shipment.driver = driver
            shipment.origin = 'Test Origin'
            shipment.destination = 'Test Destination'
            shipment.kilometrage = 12.5
            shipment.description = 'Seeded test shipment'
            shipment.save()
            self.stdout.write(f'Updated Shipment {shipment.id_shipment} with expedition-like data')
        else:
            shipment = Shipment.objects.create(
                package=pkg,
                zone='NATIONAL',
                speed='NORMAL',
                distance=12.5,
                shipment_date=timezone.now().date(),
                driver=driver,
                origin='Test Origin',
                destination='Test Destination',
                kilometrage=12.5,
                description='Seeded test shipment'
            )
            self.stdout.write(f'Created Shipment {shipment.id_shipment} with expedition-like data')

        self.stdout.write('\nSummary:')
        self.stdout.write(f' Client: {client.email} / password (plain): {client_password}')
        self.stdout.write(f' Driver: {driver.email} / password (plain): {driver_password}')
        self.stdout.write(f' Tracking number: {pkg.tracking_number}')
        self.stdout.write('Seeding complete.')
