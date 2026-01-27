from django.shortcuts import render, get_object_or_404
from .models import Shipment
from decimal import Decimal


def shipment_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, id_shipment=shipment_id)
    
    context = {
        'shipment': shipment,
        'montant_ht': shipment.montant_ht(),
        'montant_tva': shipment.montant_tva(),
        'montant_ttc': shipment.montant_ttc(),
    }
    
    return render(request, 'shipment_detail.html', context)

def shipment_amounts(request, shipment_id):
    shipment = get_object_or_404(Shipment, id_shipment=shipment_id)
    data = {
        'montant_ht': float(shipment.montant_ht()),
        'montant_tva': float(shipment.montant_tva()),
        'montant_ttc': float(shipment.montant_ttc()),
    }
    return JsonResponse(data)
