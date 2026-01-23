from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from database.models import Agent


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


@require_POST
def agent_login(request):
    """Authenticate an Agent (agent/admin) via POST and return JSON with role."""
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'error': 'missing_fields'}, status=400)

    try:
        agent = Agent.objects.get(email=email)
    except Agent.DoesNotExist:
        return JsonResponse({'success': False}, status=401)

    if agent.verifier_mot_de_passe(password):
        request.session['role'] = agent.role
        request.session['user_id'] = agent.agent_id
        try:
            agent.mettre_a_jour_connexion()
        except Exception:
            pass
        return JsonResponse({'role': agent.role})

    return JsonResponse({'success': False}, status=401)
