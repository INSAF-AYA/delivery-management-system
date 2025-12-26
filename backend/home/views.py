from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def login(request):
    return render(request, 'login.html')


def login_agent(request):
    return render(request, 'loginagent.html')


def login_client(request):
    return render(request, 'loginclient.html')


def login_driver(request):
    return render(request, 'logindriver.html')
