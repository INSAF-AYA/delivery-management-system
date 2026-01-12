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

# CLASS RECLAMATION
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

# CLASS INCIDENT
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

# CLASS AGENT 
class Agent(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),   # Admin (fait tout + système)
        ('agent', 'Agent Transport')  # Utilisateur principal (fait tout)
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
    # UN SEUL RÔLE : soit 'agent', soit 'admin'
    role = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES, 
        default='agent',
        verbose_name="Rôle"
    )
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    date_embauche = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")

    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        ordering = ['nom', 'prenom']
        db_table = 'agent'
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
         # Génération ID Agent
        if not self.agent_id:
            with transaction.atomic():
                last_obj = Agent.objects.select_for_update().filter(
                    agent_id__startswith='AG'
                ).order_by('-agent_id').first()
                
                if last_obj and last_obj.agent_id:
                    m = re.search(r"AG(\d+)$", last_obj.agent_id)
                    next_num = int(m.group(1)) + 1 if m else 1
                else:
                    next_num = 1
                self.agent_id = f"AG{next_num:04d}"
     # Hasher le mot de passe  (seulement si nouveau ou modifié)
        if self.pk is None or 'mot_de_passe' in kwargs.get('update_fields', []):
            if not self.mot_de_passe.startswith('pbkdf2_'):
                self.mot_de_passe = make_password(self.mot_de_passe)
        
        super().save(*args, **kwargs)

      # Méthodes d'authentification
    def verifier_mot_de_passe(self, mot_de_passe): 
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.
        
        Args:
            mot_de_passe (str): Mot de passe en clair à vérifier
            
        Returns:
            bool: True si le mot de passe est correct
        """
        return check_password(mot_de_passe, self.mot_de_passe)
    
    def changer_mot_de_passe(self, nouveau_mot_de_passe):
        """
        Change le mot de passe de l'agent.
        
        Args:
            nouveau_mot_de_passe (str): Nouveau mot de passe en clair
        """
        self.mot_de_passe = make_password(nouveau_mot_de_passe)
        self.save()
    
    def mettre_a_jour_connexion(self):
        self.derniere_connexion = timezone.now()
        self.save(update_fields=['derniere_connexion'])
    
      # === PROPRIÉTÉS UTILES ===
    @property
    def nom_complet(self):
        """Retourne le nom complet de l'agent (Nom Prénom)."""
        return f"{self.nom} {self.prenom}"
    # === DEUX PROPRIÉTÉS SIMPLES ===
    @property
    def est_agent(self):
        return self.role == 'agent'
    
    @property
    def est_admin(self):
        return self.role == 'admin'
    
    # === ACCÈS AUX SECTIONS ===
    # L'AGENT a accès à TOUTES les sections fonctionnelles
    # L'ADMIN a accès à TOUT (fonctionnel + système)
    
    @property
    def peut_acceder_favoris(self):
        """Section 0: Favoris - Tous peuvent personnaliser"""
        return True  # Tous les agents
    
    @property
    def peut_acceder_tables(self):
        """Section 1: Tables - Accès complet mentionné"""
        return True  # Tous les agents
    
    @property
    def peut_gerer_expeditions(self):
        """Section 2: Expéditions - Pour 'l'agent de transport'"""
        return True  # Tous les agents
    
    @property
    def peut_gerer_factures(self):
        """Section 3: Facturation - Pour gérer les paiements"""
        return True  # Tous les agents
    
    @property
    def peut_gerer_incidents(self):
        """Section 4: Incidents - Pour enregistrer/traiter"""
        return True  # Tous les agents
    
    @property
    def peut_gerer_reclamations(self):
        """Section 5: Réclamations - Pour traiter les réclamations"""
        return True  # Tous les agents
    
    @property
    def peut_voir_analytiques(self):
        """Section 6: Tableaux de bord - Pour 'les responsables'"""
        return True  # Tous les agents sont des "responsables" fonctionnels
    
    # === ACCÈS SYSTÈME (UNIQUEMENT ADMIN) ===
    @property
    def peut_gerer_utilisateurs(self):
        """Gérer les comptes agents - Admin seulement"""
        return self.est_admin
    
    @property
    def peut_configurer_systeme(self):
        """Configuration système - Admin seulement"""
        return self.est_admin
    
    @property
    def peut_voir_logs_systeme(self):
        """Voir les logs système - Admin seulement"""
        return self.est_admin
    
    @property
    def peut_faire_sauvegarde(self):
        """Faire des sauvegardes - Admin seulement"""
        return self.est_admin
    
    # === PERMISSIONS SPÉCIFIQUES ===
    def peut_supprimer(self, objet_type):
        """Vérifier les permissions de suppression"""
        permissions_suppression = {
            'client': self.est_admin,  # Seul admin peut supprimer un client
            'expedition': True,  # Tous peuvent supprimer si pas dans tournée
            'facture': self.est_admin,  # Seul admin peut supprimer facture
            'paiement': self.est_admin,  # Seul admin peut supprimer paiement
            'incident': True,  # Tous peuvent supprimer incidents
            'reclamation': True,  # Tous peuvent supprimer réclamations
        }
        return permissions_suppression.get(objet_type, False)
    def peut_imprimer(self, document_type):
        """Vérifier les permissions d'impression
         Args:
            document_type (str): Type de document à imprimer
         Returns:
            bool: True si l'agent peut imprimer ce document
        """
        # Tous les agents peuvent imprimer
        imprimables = ['bon_expedition', 'facture', 'recu', 'liste_clients', 
                      'liste_chauffeurs', 'liste_vehicules', 'rapport']
        return document_type in imprimables
    
    def peut_generer_rapport(self, rapport_type):
        """Vérifier les permissions de génération de rapports
         Args:
            rapport_type (str): Type de rapport à générer
         Returns:
            bool: True si l'agent peut générer ce rapport
        """
        # Tous les agents peuvent générer des rapports
        rapports_autorises = ['expeditions', 'factures', 'paiements', 'incidents', 
                             'reclamations', 'performance', 'analytique']
        return rapport_type in rapports_autorises



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

