from django.test import Client
from database.models import Chauffeur, Shipment

c = Client()

d = Chauffeur.objects.first()
print('driver:', d and d.id_chauffeur)

s = None
if d:
    s = Shipment.objects.filter(driver=d).first()
    print('initial assigned shipment:', s and s.id_shipment)

if not s and d:
    s2 = Shipment.objects.filter(driver__isnull=True).first()
    if s2:
        s2.driver = d
        s2.save()
        s = s2
        print('assigned a shipment:', s.id_shipment)

if not d or not s:
    print('Missing driver or shipment; aborting')
else:
    session = c.session
    session['role'] = 'driver'
    session['user_id'] = d.id_chauffeur
    session.save()

    r = c.get('/driver/')
    print('GET /driver/ ->', r.status_code)
    csrftoken = c.cookies.get('csrftoken')
    print('csrftoken cookie:', csrftoken)

    post = c.post('/driver/update_status/', {'shipment_id': s.id_shipment, 'action': 'delivered'}, HTTP_X_CSRFTOKEN=csrftoken.value if csrftoken else '')
    print('POST ->', post.status_code, post.content)

    s.refresh_from_db()
    print('after statut=', s.statut)
