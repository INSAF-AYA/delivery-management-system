from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Invoice
from database.models import Client
from database.models import Shipment
from .forms import InvoiceForm
from django.utils import timezone
import os
from django.conf import settings

def invoice_list(request):
    invoices = Invoice.objects.all()
    clients = Client.objects.all()
    shipments = Shipment.objects.filter(invoice__isnull=True)  # Only shipments without invoice
    return render(request, 'invoice/invoice_list.html', {
        'invoices': invoices,
        'clients': clients,
        'shipments': shipments,
    })

def invoice_add(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        client = get_object_or_404(Client, pk=data.get('client_id'))
        shipment = get_object_or_404(Shipment, pk=data.get('shipment_id'))
        total_amount = float(data.get('total_amount', 0))
        invoice_date = data.get('invoice_date', timezone.now().date())
        invoice_pdf = None  # File upload handled separately if needed

        invoice = Invoice(client=client, shipment=shipment, total_amount=total_amount, invoice_date=invoice_date)
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
    if invoice.invoice_pdf and os.path.exists(invoice.invoice_pdf.path):
        with open(invoice.invoice_pdf.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(invoice.invoice_pdf.name)}"'
            return response
    return HttpResponse("File not found", status=404)
