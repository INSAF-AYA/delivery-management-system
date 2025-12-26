from django.shortcuts import render


def index(request):
    return render(request, 'DASHindex.html')


def dashboard_clients(request):
    return render(request, 'DASHclients.html')


def dashboard_shipments(request):
    return render(request, 'DASHshipments.html')


def drivers(request):
    return render(request, 'drivers.html')


def vehicles(request):
    return render(request, 'vehicles.html')


def incidents(request):
    return render(request, 'incidents.html')


def invoices(request):
    return render(request, 'invoices.html')


def package(request):
    return render(request, 'package.html')
