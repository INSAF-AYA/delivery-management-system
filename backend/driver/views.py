from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from database.models import Chauffeur


def index(request):
    return render(request, 'driver.html')


@require_POST
def driver_login(request):
    """Authenticate a Chauffeur (driver) via POST form."""
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'error': 'missing_fields'}, status=400)

    try:
        driver = Chauffeur.objects.get(email=email)
    except Chauffeur.DoesNotExist:
        return JsonResponse({'success': False}, status=401)

    if driver.check_password_driver(password):
        request.session['role'] = 'driver'
        request.session['user_id'] = driver.id_chauffeur
        return JsonResponse({'success': True, 'role': 'driver'})

    return JsonResponse({'success': False}, status=401)
