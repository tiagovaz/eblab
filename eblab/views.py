from django.http import HttpResponse
from eblab.models import RFIDTag, Log, Person, Event
import datetime

def rfid_auth(request):
    if request.method == 'GET':
        uid = request.GET.get('uid', '')
        resource = request.GET.get('resource', '')
        action = request.GET.get('action', '')

        # If the RFID tag is in the database
        if RFIDTag.objects.filter(uid=uid).exists():
            rfidtag_obj = RFIDTag.objects.get(uid=uid)
            event_obj = Event.objects.get(event=action)

            # Laser cutter access
            if resource == 'laser_cutter':
                if action == 'NON': # no db action, just auth request
                    if rfidtag_obj.laser_cutter_access:
                        return HttpResponse("Authorized", status=200)
                    else:
                        return HttpResponse(status=405)
                else: # log into database
                    log_obj = Log()
                    log_obj.event = event_obj
                    log_obj.date = datetime.datetime.now()
                    log_obj.rfid = rfidtag_obj
                    log_obj.person = rfidtag_obj.person.all()[0]
                    log_obj.save()
                    return HttpResponse("Logged", status=200)
            else: # unknown resource
                return HttpResponse(status=406)
        # Tag invalid / not found
        else:
            return HttpResponse(status=406)

        

def index(request):
    return HttpResponse('index')
