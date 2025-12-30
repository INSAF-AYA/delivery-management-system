from django.db import models, transaction
from django.contrib.auth.hashers import make_password, check_password
import secrets
import string
import re


# =========================
#        CLIENT
# =========================
class Client(models.Model):
    """
    Modèle Client.
    Le client est créé par l'administration.
    Le mot de passe est généré automatiquement et stocké de façon chiffrée.
    """

    # Identifiant automatique (ex: CL000001)
    id_client = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    # Mot de passe chiffré (hashé)
    password_client = models.CharField(max_length=128)

    # Informations personnelles
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, unique=True)

    # Adresse
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, blank=True)

    # Date d'inscription automatique
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.email})"

    def generate_password(self, length=8):
        """
        Génère un mot de passe aléatoire,
        le chiffre et le stocke en base de données.
        Retourne le mot de passe en clair pour le donner au client.
        """
        chars = string.ascii_letters + string.digits
        raw_password = ''.join(secrets.choice(chars) for _ in range(length))
        self.password_client = make_password(raw_password)
        return raw_password

    def check_password(self, raw_password):
        """
        Vérifie si le mot de passe fourni est correct.
        """
        return check_password(raw_password, self.password_client)

    def save(self, *args, **kwargs):
        """
        Génère automatiquement l'id_client (CL000001, CL000002, ...)
        """
        if not self.id_client:
            with transaction.atomic():
                last_client = Client.objects.select_for_update().filter(
                    id_client__startswith='CL'
                ).order_by('-id_client').first()

                if last_client:
                    match = re.search(r"CL(\d+)$", last_client.id_client)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                self.id_client = f"CL{next_num:06d}"

        super().save(*args, **kwargs)


# =========================
#        VEHICULE
# =========================
class Vehicule(models.Model):
    """
    Modèle Véhicule.
    """

    # Identifiant automatique (ex: VH000001)
    id_vehicule = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=100, blank=True)

    # Capacité de charge en kg
    capacite_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Capacité en kg"
    )

    # Consommation en L/100km
    consommation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="L/100km"
    )

    etat = models.CharField(
        max_length=40,
        default="disponible",
        blank=True
    )

    date_mise_service = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"

    def __str__(self):
        return f"{self.id_vehicule} - {self.immatriculation}"

    def save(self, *args, **kwargs):
        """
        Génère automatiquement l'id_vehicule (VH000001, VH000002, ...)
        """
        if not self.id_vehicule:
            with transaction.atomic():
                last_vehicule = Vehicule.objects.select_for_update().order_by('-id_vehicule').first()

                if last_vehicule:
                    match = re.search(r"VH(\d+)$", last_vehicule.id_vehicule)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                self.id_vehicule = f"VH{next_num:06d}"

        super().save(*args, **kwargs)


# =========================
#        SERVICE
# =========================
class Service(models.Model):
    """
    Modèle Service de livraison.
    """

    speed = models.CharField(
        max_length=20,
        choices=[
            ('NORMAL', 'Normal'),
            ('EXPRESS', 'Express'),
        ],
        default='NORMAL'
    )

    zone = models.CharField(
        max_length=20,
        choices=[
            ('NATIONAL', 'National'),
            ('INTERNATIONAL', 'International'),
        ],
        default='NATIONAL'
    )

    def __str__(self):
        return f"{self.speed} - {self.zone}"
