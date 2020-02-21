from datetime import datetime
from django.db.models.signals import post_save
import pytz

def calculate_usage(sender, instance, **kwargs):
    from eblab.models import Log, Event
    last_log = Log.objects.all().order_by('-id')[1]
    last_log_date = last_log.date
    # if user has logged off
    if instance.event.event == 'LOO':
        # just confirming that was the same user and was a login
        if instance.person == last_log.person and last_log.event.event == 'LOI':
            logoff_date = instance.date
            print("DATES:", last_log_date, logoff_date)
            usage = logoff_date - last_log_date
            print("USAGE", usage)
            instance.logged_time = str(usage)
            post_save.disconnect(calculate_usage, sender=sender)
            instance.save()
            post_save.connect(calculate_usage, sender=Log)
    # if user finished using the laser printer
    elif instance.event.event == 'LAE':
        if instance.person == last_log.person and last_log.event.event == 'LAS':
            laser_end_date = instance.date
            laser_usage = laser_end_date - last_log_date
            instance.laser_usage_time = str(laser_usage)
            post_save.disconnect(calculate_usage, sender=sender)
            instance.save()
            post_save.connect(calculate_usage, sender=Log)
