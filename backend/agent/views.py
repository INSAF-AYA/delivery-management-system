from django.shortcuts import render
from django.http import JsonResponse
from database.models import Agent
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required
def agent_list(request):
    if request.method == "GET":
        agents = Agent.objects.all().order_by("nom", "prenom")
        data = [
            {
                "agent_id": a.agent_id,
                "nom": a.nom,
                "prenom": a.prenom,
                "telephone": a.telephone,
                "date_embauche": a.date_embauche.strftime("%Y-%m-%d") if a.date_embauche else "",
                "role": a.role
            }
            for a in agents
        ]
        return JsonResponse({"agents": data})

@login_required
def add_agent(request):
    if request.method == "POST":
        user = request.user.agent
        if not user.est_admin:
            return JsonResponse({"success": False, "error": "Only admin can add agents"})

        try:
            nom = request.POST.get("agent_name")
            prenom = request.POST.get("agent_prenom")
            email = request.POST.get("email")
            telephone = request.POST.get("Phone_number")
            mot_de_passe = request.POST.get("password")
            date_embauche = request.POST.get("HiringDate")
            role = request.POST.get("type").lower() if request.POST.get("type") else "agent"

            agent = Agent(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                mot_de_passe=mot_de_passe,
                date_embauche=date_embauche,
                role=role
            )
            agent.save()
            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@login_required
def delete_agent(request):
    if request.method == "POST":
        user = request.user.agent
        if not user.est_admin:
            return JsonResponse({"success": False, "error": "Only admin can delete agents"})

        try:
            agent_id = request.POST.get("Agent_id")
            agent = Agent.objects.get(agent_id=agent_id)
            agent.delete()
            return JsonResponse({"success": True})
        except Agent.DoesNotExist:
            return JsonResponse({"success": False, "error": "Agent not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
