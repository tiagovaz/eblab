from datetime import datetime
import pytz

def calculate_usage(sender, instance, **kwargs):
    from eblab.models import Log, Event
    login_date = Log.objects.all().order_by('-id')[1].date
    logoff_date = instance.date
    print("DATES:", login_date, logoff_date)
    usage = logoff_date - login_date
    print("USAGE", usage)

