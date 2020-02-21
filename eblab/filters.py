
from django_filters import ModelChoiceFilter, ModelMultipleChoiceFilter, MultipleChoiceFilter, ChoiceFilter, FilterSet, CharFilter, NumberFilter
from .models import Log, Event, Person, RFIDTag, LogDaily
from functools import reduce
from django.db.models import Q

class LogFilter(FilterSet):
    event = ModelChoiceFilter(queryset=Event.objects.all())
    person = ModelChoiceFilter(queryset=Person.objects.all())
    rfid = ModelChoiceFilter(queryset=RFIDTag.objects.all())

    class Meta:
        model = Log
        fields = ['rfid', 'event', 'person']

class LogFilterDaily(FilterSet):
    person = ModelChoiceFilter(queryset=Person.objects.all())
    rfid = ModelChoiceFilter(queryset=RFIDTag.objects.all())

    class Meta:
        model = LogDaily
        fields = ['rfid', 'person']
