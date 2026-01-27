from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from database.models import Invoice, Client, Shipment
from database.models import Client
from database.models import Shipment
from .forms import InvoiceForm
from django.utils import timezone
import os
from django.conf import settings

def invoice_list(request):
    invoices = Invoice.objects.all()
    clients = Client.objects.all()
    shipments = Shipment.objects.all()
    print("Available shipments:", shipments)  # DEBUG
    return render(request, 'invoices.html', {
        'invoices': invoices,
        'clients': clients,
        'shipments': shipments,
    })

def invoice_add(request):
    if request.method == 'POST':
        client = get_object_or_404(Client, pk=request.POST.get('client_id'))
        shipment = get_object_or_404(Shipment, pk=request.POST.get('shipment_id'))
        total_amount = float(request.POST.get('total_amount', 0))
        invoice_date = request.POST.get('invoice_date', timezone.now().date())
        invoice_pdf = request.FILES.get('invoice_pdf')  # <-- get the uploaded file

        invoice = Invoice(
            client=client,
            shipment=shipment,
            total_amount=total_amount,
            invoice_date=invoice_date,
            invoice_pdf=invoice_pdf
        )
        invoice.save()
        return JsonResponse({'success': True, 'id_invoice': invoice.id_invoice})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def invoice_detail_json(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    data = {
        'success': True,
        'invoice': {
            'id_invoice': invoice.id_invoice,
            'client': f"{invoice.client.nom} {invoice.client.prenom}",
            'shipment': invoice.shipment.id_shipment,
            'total_amount': str(invoice.total_amount),
            'invoice_date': str(invoice.invoice_date)
        }
    }
    return JsonResponse(data)

def invoice_delete(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice.delete()
    return JsonResponse({'success': True})

def invoice_download(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    if not invoice.invoice_pdf:
        return HttpResponse("No PDF attached to this invoice", status=404)

    if not os.path.exists(invoice.invoice_pdf.path):
        return HttpResponse("PDF missing on server", status=404)

    with open(invoice.invoice_pdf.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{os.path.basename(invoice.invoice_pdf.name)}"'
        )
        return response


def shipment_amounts(request, shipment_id):
    shipment = Shipment.objects.get(id_shipment=shipment_id)
    data = {
        'montant_ht': float(shipment.montant_ht()),
        'montant_tva': float(shipment.montant_tva()),
        'montant_ttc': float(shipment.montant_ttc()),
    }
    return JsonResponse(data)
