from django.http import HttpResponse
from eblab.models import RFIDTag

def rfid_auth(request):
    if request.method == 'GET':
        uid = request.GET.get('uid', '')
        resource = request.GET.get('resource', '')
        action = request.GET.get('action', '')

        # If the RFID tag is in the database
        if RFIDTag.objects.filter(uid=uid).exists():
            rfidtag_obj = RFIDTag.objects.get(uid=uid)

            # Main door access
            if resource == 'main_door':
                if rfidtag_obj.main_door_access:
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=405)

            # Laser cutter access
            elif resource == 'laser_cutter':
                if rfidtag_obj.laser_cutter_access:
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=405)
            else:
                return HttpResponse(status=406)

        # Tag invalid / not found
        else:
            return HttpResponse(status=406)

def index(request):
    return HttpResponse('index')
