from django.db import models

class RFIDTag(models.Model):
    uid = models.CharField(max_length=8)
    main_door_access = models.BooleanField(default=False)
    laser_cutter_access = models.BooleanField(default=False)

    def __str__(self):
        return self.uid

class Person(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    rfid_tag = models.ForeignKey('RFIDTag', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
