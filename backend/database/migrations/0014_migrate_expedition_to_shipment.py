# Generated manually to migrate Expedition data model into Shipment
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0013_chauffeur_vehicule'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to='database.client'),
        ),
        migrations.AddField(
            model_name='shipment',
            name='origin',
            field=models.CharField(blank=True, max_length=150, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shipment',
            name='destination',
            field=models.CharField(blank=True, max_length=150, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shipment',
            name='kilometrage',
            field=models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=8),
        ),
        migrations.AddField(
            model_name='shipment',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipments', to='database.chauffeur'),
        ),
        migrations.AddField(
            model_name='shipment',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shipment',
            name='statut',
            field=models.CharField(default='PENDING', max_length=20),
        ),
        migrations.DeleteModel(
            name='Expedition',
        ),
    ]
