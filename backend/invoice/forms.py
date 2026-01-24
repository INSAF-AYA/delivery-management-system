from django import forms
from .models import Invoice
from database.models import Client
from database.models import Shipment

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'shipment', 'total_amount', 'invoice_date', 'invoice_pdf']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
