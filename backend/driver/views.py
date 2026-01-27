from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db import transaction
from django.middleware.csrf import get_token
from django.conf import settings
import logging

from database.models import Chauffeur, Shipment

logger = logging.getLogger(__name__)

# =========================
# Login (CLASSIC)
# =========================
def driver_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # detect JSON / AJAX clients (front-end sets Accept: application/json)
        wants_json = 'application/json' in request.META.get('HTTP_ACCEPT', '')

        if not email or not password:
            if wants_json:
                return JsonResponse({"success": False, "error": "missing_fields"}, status=400)
            return render(request, "login.html", {
                "error": "Please fill all fields"
            })

        try:
            driver = Chauffeur.objects.get(email=email)
        except Chauffeur.DoesNotExist:
            if wants_json:
                return JsonResponse({"success": False, "error": "invalid_credentials"}, status=401)
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

        if not driver.check_password_driver(password):
            if wants_json:
                return JsonResponse({"success": False, "error": "invalid_credentials"}, status=401)
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

        # ✅ create session
        request.session["role"] = "driver"
        request.session["user_id"] = driver.id_chauffeur
        request.session.modified = True

        if wants_json:
            return JsonResponse({"success": True, "role": "driver"})

        return redirect("driver_index")

    return render(request, "login.html")


# =========================
# Logout
# =========================
def driver_logout(request):
    request.session.flush()
    return redirect("driver_login")


# =========================
# Dashboard
# =========================
def index(request):
    if request.session.get("role") != "driver":
        return redirect("driver_login")

    user_id = request.session.get("user_id")
    today = timezone.localdate()

    try:
        driver = Chauffeur.objects.get(id_chauffeur=user_id)
    except Chauffeur.DoesNotExist:
        return redirect("driver_login")

    todays_shipments = Shipment.objects.filter(
        driver=driver,
        shipment_date=today
    )

    unassigned_shipments = Shipment.objects.filter(
        driver__isnull=True,
        shipment_date=today
    )

    assigned_shipments = Shipment.objects.filter(driver=driver)

    # Shipments completed today by this driver (used in template)
    completed_today = todays_shipments.filter(statut="DELIVERED")

    get_token(request)  # CSRF for AJAX buttons

    return render(request, "driver.html", {
        "driver": driver,
        "todays_shipments": todays_shipments,
        "unassigned_shipments": unassigned_shipments,
        "assigned_shipments": assigned_shipments,
        "completed_today": completed_today,
        "pending": todays_shipments.filter(statut="PENDING").count(),
        "completed": todays_shipments.filter(statut="DELIVERED").count(),
        "total": todays_shipments.count(),
    })


# =========================
# Ping (debug)
# =========================
@require_GET
def ping(request):
    return JsonResponse({
        "role": request.session.get("role"),
        "user_id": request.session.get("user_id"),
        "cookies": request.COOKIES
    })


# =========================
# Claim shipment
# =========================
@require_POST
def claim_shipment(request):
    if request.session.get("role") != "driver":
        return JsonResponse({"success": False}, status=403)

    shipment_id = request.POST.get("shipment_id")
    driver = Chauffeur.objects.get(id_chauffeur=request.session["user_id"])

    with transaction.atomic():
        shipment = Shipment.objects.select_for_update().get(id_shipment=shipment_id)
        if shipment.driver:
            return JsonResponse({"success": False, "error": "already_assigned"})
        shipment.driver = driver
        shipment.save()

    return JsonResponse({"success": True})


# =========================
# Update shipment status
# =========================
@require_POST
def update_shipment_status(request):
    logger.debug("update_shipment_status called: session_role=%s user_id=%s", request.session.get("role"), request.session.get("user_id"))

    wants_json = 'application/json' in request.META.get('HTTP_ACCEPT', '')

    if request.session.get("role") != "driver":
        logger.warning("update_shipment_status forbidden: wrong role or not logged in")
        if wants_json:
            return JsonResponse({"success": False, "error": "forbidden"}, status=403)
        return redirect('driver_login')

    shipment_id = request.POST.get("shipment_id")
    action = request.POST.get("action")
    logger.debug("update_shipment_status params: shipment_id=%s action=%s", shipment_id, action)

    action_map = {
        "delivered": "DELIVERED",
        "delayed": "IN_TRANSIT",
        "failed": "FAILED",
    }

    if not action or action not in action_map:
        logger.warning("update_shipment_status bad request: invalid action=%s", action)
        return JsonResponse({"success": False, "error": "invalid_action"}, status=400)

    try:
        with transaction.atomic():
            try:
                shipment = Shipment.objects.select_for_update().get(id_shipment=shipment_id)
            except Shipment.DoesNotExist:
                logger.warning("update_shipment_status: shipment not found %s", shipment_id)
                return JsonResponse({"success": False, "error": "not_found"}, status=404)

            if str(shipment.driver_id) != str(request.session.get("user_id")):
                logger.warning("update_shipment_status forbidden: shipment %s driver mismatch (owner=%s session=%s)", shipment_id, shipment.driver_id, request.session.get("user_id"))
                return JsonResponse({"success": False, "error": "forbidden"}, status=403)

            shipment.statut = action_map[action]
            shipment.save()

    except Exception as e:
        logger.exception("update_shipment_status failed: %s", e)
        return JsonResponse({"success": False, "error": "server_error"}, status=500)

    logger.info("update_shipment_status: shipment %s set to %s by user %s", shipment_id, action_map[action], request.session.get("user_id"))
    if wants_json:
        return JsonResponse({"success": True})
    # Non-AJAX form submit -> redirect back to dashboard
    return redirect('driver_index')
