from datetime import datetime
from django.db.models.signals import post_save
import pytz

def calculate_usage(sender, instance, **kwargs):
    from eblab.models import Log, LogDaily
    # if user has logged off
    if instance.event.event == 'LOO':
        # last login
        last_log = Log.objects.filter(event__event='LOI').latest('date')
        last_log_date = last_log.date
        # just confirming that was the same user
        if instance.person == last_log.person:
            logoff_date = instance.date
            print(logoff_date, last_log_date)
            usage = logoff_date.replace(tzinfo=None) - last_log_date.replace(tzinfo=None)
            instance.logged_time = usage
            post_save.disconnect(calculate_usage, sender=sender)
            instance.save()
            post_save.connect(calculate_usage, sender=Log)
            log_daily, created = LogDaily.objects.get_or_create(person=instance.person, rfid=instance.rfid, date=instance.date.date())
            if log_daily.usage_time:
                log_daily.usage_time = log_daily.usage_time + usage
            else:
                log_daily.usage_time = usage
            log_daily.save()
    elif instance.event.event == 'LAE':
        if log_daily.laser_usage_time:
            log_daily.laser_usage_time = log_daily.laser_usage_time + instance.laser_usage_time
        else:
            log_daily.laser_usage_time = laser_usage
        log_daily.save()
