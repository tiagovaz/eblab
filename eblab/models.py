from django.db import models
from django.db.models.signals import post_save
from eblab import signals

class RFIDTag(models.Model):
    uid = models.CharField(max_length=8, unique=True)
    main_door_access = models.BooleanField(default=False)
    laser_cutter_access = models.BooleanField(default=False)

    def __str__(self):
        return self.uid

class Person(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    rfid_tag = models.ForeignKey('RFIDTag', related_name='person', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

class LogDaily(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    rfid = models.ForeignKey('RFIDTag', on_delete=models.CASCADE)
    date = models.DateField()
    usage_time = models.DurationField(null=True, blank=True)
    laser_usage_time = models.DurationField(null=True, blank=True)

class Event(models.Model):
    LASER_START = 'LAS'
    LASER_END = 'LAE'
    LOGGED_IN = 'LOI'
    LOGGED_OUT = 'LOO'
    NONE = 'NON'
    EVENT_CHOICES = [
        (LASER_START, 'Laser on'),
        (LASER_END, 'Laser off'),
        (LOGGED_IN, 'Logged in'),
        (LOGGED_OUT, 'Logged out'),
        (NONE, 'No action'),
    ]
    event = models.CharField(
        max_length=3,
        choices=EVENT_CHOICES,
        default=NONE,
    )

    def __str__(self):
        return "%s" % self.get_event_display()

class Log(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    rfid = models.ForeignKey('RFIDTag', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    date = models.DateTimeField()
    logged_time = models.DurationField(blank=True, null=True)
    laser_usage_time = models.DurationField(blank=True, null=True)
    
    def __str__(self):
        return "%s RFID %s %s at %s" % (self.person, self.rfid, self.event, self.date)

models.signals.post_save.connect(
    signals.calculate_usage,
    sender=Log
)


