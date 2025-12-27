from django.db import models, transaction
from django.db.models import Max
import re


class Client(models.Model):

    id_client = models.CharField(max_length=12, primary_key=True, editable=False)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.id_client:
           
            with transaction.atomic():
                last_obj = Client.objects.select_for_update().filter(
                    id_client__startswith='CL'
                ).order_by('-id_client').first()

                if last_obj and last_obj.id_client:
                    m = re.search(r"CL(\d+)$", last_obj.id_client)
                    next_num = int(m.group(1)) + 1 if m else 1
                else:
                    next_num = 1

                self.id_client = f"CL{next_num:06d}"

        super().save(*args, **kwargs)



class Vehicule(models.Model):

    id_vehicule = models.CharField(
        max_length=12,
        primary_key=True,
        editable=False
    )

    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=100, blank=True)
    capacite_charge = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Capacité en kg"
    )
    consommation = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="L/100km"
    )
    etat = models.CharField(max_length=40, default="disponible", blank=True)
    date_mise_service = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"

    def __str__(self):
        return f"{self.id_vehicule} - {self.immatriculation}"

    def save(self, *args, **kwargs):
        if not self.id_vehicule:
            with transaction.atomic():
                last_obj = Vehicule.objects.select_for_update().order_by('-id_vehicule').first()

                if last_obj and last_obj.id_vehicule:
                    m = re.search(r"VH(\d+)$", last_obj.id_vehicule)
                    next_num = int(m.group(1)) + 1 if m else 1
                else:
                    next_num = 1

                self.id_vehicule = f"VH{next_num:06d}"

        super().save(*args, **kwargs)

class Service(models.Model):
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