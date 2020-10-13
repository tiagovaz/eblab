from rest_framework import serializers
from eblab.models import Person, LogDaily

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'first_name', 'last_name', 'email', 'rfid_tag')

class LogDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogDaily
        fields = ('id', 'person', 'rfid', 'date', 'usage_time', 'laser_usage_time')
