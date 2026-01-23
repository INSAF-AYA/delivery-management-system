from django.db import models, transaction
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone 
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

    # Véhicule affecté (optionnel)
    vehicule = models.ForeignKey(
        'Vehicule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chauffeurs'
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

# =========================
#        RECLAMATION
# =========================
class Reclamation(models.Model):
   RECLAMATION_STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
        ('pending_customer', 'Pending Customer Response'),
        ('closed', 'Closed'),
    ]
   id_reclamation = models.CharField(primary_key=True, max_length=10, verbose_name="Reclamation ID",editable=False)
   date_reclamation= models.DateTimeField(default=timezone.now, verbose_name="Reclamation Date")
   created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
   updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
   
   nature = models.CharField(max_length=255, verbose_name="Nature")
   description = models.TextField(verbose_name="Description", blank=True)

   status = models.CharField(
        max_length=50, 
        choices=RECLAMATION_STATUS_CHOICES, 
        default='new',
        verbose_name="Status"
    )
   commentaire = models.TextField(blank=True, verbose_name="Commentaire")
   class Meta:
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"
        ordering = ['-date_reclamation']
        db_table = 'reclamation'  # Nom de la table en base
    
   def __str__(self):
        return f"Réclamation {self.id_reclamation} - {self.nature}"
   def save(self, *args, **kwargs):
        # Génération ID Réclamation
        if not self.id_reclamation:
            with transaction.atomic():
                last_obj = Reclamation.objects.select_for_update().filter(
                    id_reclamation__startswith='REC'
                ).order_by('-id_reclamation').first()

                if last_obj and last_obj.id_reclamation:
                    m = re.search(r"REC(\d+)$", last_obj.id_reclamation)
                    next_num = int(m.group(1)) + 1 if m else 1
                else:
                    next_num = 1
                self.id_reclamation = f"REC{next_num:06d}" 
        super().save(*args, **kwargs)

# =========================
#        INCIDENT
# =========================
class Incident(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('delay', 'Delay'),
        ('loss', 'Package Loss'),
        ('damage', 'Damage'),
        ('technical', 'Technical Problem'),
        ('accident', 'Accident'),
        ('other', 'Other'),
    ]
    
    INCIDENT_STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    id_incident = models.CharField(
        primary_key=True,
        max_length=10,
        verbose_name="Incident ID",
        editable=False
    )
    
    incident_type = models.CharField(
        max_length=50, 
        choices=INCIDENT_TYPE_CHOICES, 
        verbose_name="Type d'incident"
    )
    description = models.TextField(verbose_name="Description")
    incident_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Date de l'incident"
    )
    status = models.CharField(
        max_length=50, 
        choices=INCIDENT_STATUS_CHOICES, 
        default='new',
        verbose_name="Status"
    )
    attachment = models.FileField(
     upload_to='incidents/attachments/',
     null=True,
     blank=True,
     verbose_name="Document ou photo joint"
    )

    commentaire = models.TextField( blank=True,verbose_name="Commentaire")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Resolution Date"
    )
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priority"
    )

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
        ordering = ['-incident_date']
        db_table = 'incident'
    
    def __str__(self):
        return f"Incident {self.id_incident} - {self.get_incident_type_display()}"
    def save(self, *args, **kwargs):
        # Génération ID Incident
        if not self.id_incident:
            with transaction.atomic():
                last_obj = Incident.objects.select_for_update().filter(
                    id_incident__startswith='INC'
                ).order_by('-id_incident').first()

                if last_obj and last_obj.id_incident:
                    m = re.search(r"INC(\d+)$", last_obj.id_incident)
                    next_num = int(m.group(1)) + 1 if m else 1
                else:
                    next_num = 1

                self.id_incident = f"INC{next_num:06d}"
        
        super().save(*args, **kwargs)
    def resolve(self,  resolution_notes=""):
         self.status = 'resolved'
         self.resolution_date = timezone.now()
         if resolution_notes:
             self.commentaire = f"{self.commentaire}\n[RESOLUTION {self.resolution_date.strftime('%Y-%m-%d %H:%M')}]: {resolution_notes}"
         self.save()
    def close(self):
        """Close the incident after resolution"""
        if self.status == 'resolved':
            self.status = 'closed'
            self.save()
    @property
    def is_active(self):
        """Check if incident is still active"""
        return self.status in ['new', 'open', 'in_progress']
    @property
    def days_open(self):
        """Calculate number of days the incident has been open"""
        if self.status in ['resolved', 'closed', 'cancelled'] and self.resolution_date:
            return (self.resolution_date - self.created_at).days
        return (timezone.now() - self.created_at).days
    

# =========================
#        AGENT
# =========================
class Agent(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('agent', 'Agent Transport')
    ]
    
    agent_id = models.CharField(
        primary_key=True,
        max_length=10,
        verbose_name="Agent ID",
        editable=False
    )

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom") 
    email = models.EmailField(unique=True, verbose_name="Email")
    mot_de_passe = models.CharField(max_length=255, verbose_name="Mot de passe (hashé)")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='agent', verbose_name="Rôle")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    date_embauche = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 🔹 Generate agent_id if it doesn't exist
        if not self.agent_id:
            with transaction.atomic():
                last_obj = Agent.objects.select_for_update().filter(agent_id__startswith='AG-').order_by('-agent_id').first()
                if last_obj and last_obj.agent_id:
                    m = re.search(r"AG-(\d+)$", last_obj.agent_id)
                    next_num = int(m.group(1)) + 1 if m else 1
                else:
                    next_num = 1
                self.agent_id = f"AG-{next_num:04d}"

        # 🔹 Hash password
        if not self.mot_de_passe.startswith('pbkdf2_'):
            self.mot_de_passe = make_password(self.mot_de_passe)

        super().save(*args, **kwargs)

    def verifier_mot_de_passe(self, raw_password):
        """Check if the provided password matches the stored hashed password."""
        return check_password(raw_password, self.mot_de_passe)

    def mettre_a_jour_connexion(self):
        """Update the last login timestamp."""
        self.date_modification = timezone.now()
        self.save(update_fields=['date_modification'])

        


# =========================
#        PACKAGE
# =========================
class Package(models.Model):

    PACKAGE_TYPE_CHOICES = [
        ('DOC', 'Documents'),
        ('ELEC', 'Electronics'),
        ('FURN', 'Furniture'),
        ('OTHER', 'Other'),
    ]

    id_package = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    tracking_number = models.CharField(
        max_length=50,
        unique=True
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='packages'
    )

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    number_of_pieces = models.PositiveIntegerField()

    package_type = models.CharField(
        max_length=10,
        choices=PACKAGE_TYPE_CHOICES
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"

    def __str__(self):
        return self.id_package

    def save(self, *args, **kwargs):
        """
        Génère automatiquement l'id_package (PCG001, PCG002, ...)
        """
        if not self.id_package:
            with transaction.atomic():
                last_obj = Package.objects.select_for_update().order_by('-id_package').first()

                if last_obj:
                    match = re.search(r"PCG(\d+)$", last_obj.id_package)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                self.id_package = f"PCG{next_num:03d}"

        super().save(*args, **kwargs)


# =========================
#        TOUR
# =========================
class Tour(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
    ]

    id_tour = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    chauffeur = models.ForeignKey(
        Chauffeur,
        on_delete=models.CASCADE,
        related_name='tours'
    )

    tour_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    shipments = models.ManyToManyField(
        'Shipment',
        blank=True,
        related_name='tours'
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    def __str__(self):
        return self.id_tour

    def save(self, *args, **kwargs):
        """
        Génère automatiquement l'id_tour (TOU001, TOU002, ...)
        """
        if not self.id_tour:
            with transaction.atomic():
                last_obj = Tour.objects.select_for_update().order_by('-id_tour').first()

                if last_obj:
                    match = re.search(r"TOU(\d+)$", last_obj.id_tour)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                self.id_tour = f"TOU{next_num:03d}"

        super().save(*args, **kwargs)


# =========================
#        INVOICE
# =========================
class Invoice(models.Model):

    id_invoice = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    shipment = models.OneToOneField(
        'Shipment',
        on_delete=models.CASCADE,
        related_name='invoice'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    invoice_date = models.DateField(default=timezone.now)

    invoice_pdf = models.FileField(
        upload_to='invoices/'
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return self.id_invoice

    def save(self, *args, **kwargs):
        """
        Génère automatiquement l'id_invoice (INV001, INV002, ...)
        """
        if not self.id_invoice:
            with transaction.atomic():
                last_obj = Invoice.objects.select_for_update().order_by('-id_invoice').first()

                if last_obj:
                    match = re.search(r"INV(\d+)$", last_obj.id_invoice)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                self.id_invoice = f"INV{next_num:03d}"

        super().save(*args, **kwargs)


# =========================
#        SHIPMENT
# =========================
class Shipment(models.Model):

    SHIPMENT_ZONE_CHOICES = [
        ('NATIONAL', 'National'),
        ('INTERNATIONAL', 'International'),
    ]

    SPEED_CHOICES = [
        ('NORMAL', 'Normal'),
        ('EXPRESS', 'Express'),
    ]

    id_shipment = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    package = models.OneToOneField(
        Package,
        on_delete=models.CASCADE,
        related_name='shipment'
    )

    # Fields migrated from the old `Expedition` model so Shipment becomes the
    # canonical delivery/expedition object in the system. All are optional to
    # preserve existing records and allow gradual backfill.
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='shipments',
        null=True,
        blank=True,
        help_text='Optional: client linked to this shipment (duplicate of package.client)'
    )

    origin = models.CharField(max_length=150, blank=True)
    destination = models.CharField(max_length=150, blank=True)

    kilometrage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Distance in kilometers (optional)'
    )

    driver = models.ForeignKey(
        'Chauffeur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments'
    )

    description = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    zone = models.CharField(
        max_length=20,
        choices=SHIPMENT_ZONE_CHOICES
    )

    speed = models.CharField(
        max_length=20,
        choices=SPEED_CHOICES
    )

    distance = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    shipment_date = models.DateField(
        null=True,
        blank=True
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Shipment"
        verbose_name_plural = "Shipments"

    def __str__(self):
        return self.id_shipment

    def save(self, *args, **kwargs):
        """
        Génère automatiquement l'id_shipment (SHP001, SHP002, ...)
        """
        if not self.id_shipment:
            with transaction.atomic():
                last_obj = Shipment.objects.select_for_update().order_by('-id_shipment').first()

                if last_obj:
                    match = re.search(r"SHP(\d+)$", last_obj.id_shipment)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                self.id_shipment = f"SHP{next_num:03d}"

        super().save(*args, **kwargs)

