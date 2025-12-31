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
STATUT_CHOICES = [
    ('actif', 'Actif'),
    ('inactif', 'Inactif'),
    ('suspendu', 'Suspendu'),
    ('en_conge', 'En congé'),
]


class Chauffeur(models.Model):

    id_chauffeur = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    password_driver = models.CharField(
        max_length=128,
        help_text="Mot de passe du chauffeur (haché)"
    )

    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=30)
    email = models.EmailField(max_length=200, unique=True)

    numero_permis = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de permis"
    )

    date_embauche = models.DateField(auto_now_add=True)

    disponibilite = models.BooleanField(default=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif'
    )

    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.id_chauffeur})"

    # 🔐 Génération du mot de passe
    def generate_password_driver(self, length=8):
        chars = string.ascii_letters + string.digits
        raw_password = ''.join(secrets.choice(chars) for _ in range(length))
        self.password_driver = make_password(raw_password)
        self.save()
        return raw_password

    def check_password_driver(self, raw_password):
        return check_password(raw_password, self.password_driver)

    #  Génération automatique de l'ID
    def save(self, *args, **kwargs):
        if not self.id_chauffeur:
            with transaction.atomic():
                last_obj = Chauffeur.objects.select_for_update().order_by('-id_chauffeur').first()
                next_num = (
                    int(re.search(r"CH(\d+)$", last_obj.id_chauffeur).group(1)) + 1
                    if last_obj else 1
                )
                self.id_chauffeur = f"CH{next_num:06d}"

        super().save(*args, **kwargs)
STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('IN_TRANSIT', 'In transit'),
    ('DELIVERED', 'Delivered'),
]


class Expedition(models.Model):

    id_expedition = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='expeditions'
    )

    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)

    kilometrage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Distance en kilomètres"
    )

    driver = models.ForeignKey(
        'Chauffeur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expeditions'
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    class Meta:
        verbose_name = "Expedition"
        verbose_name_plural = "Expeditions"

    def __str__(self):
        return f"{self.id_expedition} - {self.statut}"

    #  Génération automatique de l'ID
    def save(self, *args, **kwargs):
        if not self.id_expedition:
            with transaction.atomic():
                last_obj = Expedition.objects.select_for_update().order_by('-id_expedition').first()
                next_num = (
                    int(re.search(r"SH(\d+)$", last_obj.id_expedition).group(1)) + 1
                    if last_obj else 1
                )
                self.id_expedition = f"SH{next_num:06d}"

        super().save(*args, **kwargs)
