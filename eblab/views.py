from django.http import HttpResponse
from eblab.models import RFIDTag, Log, Person, Event, LogDaily
from django.views.generic import TemplateView
from .filters import LogFilter, LogFilterDaily
from django_tables2 import RequestConfig
from django_tables2.export.views import ExportMixin
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div
import django_tables2
import datetime
from django.core.mail import send_mail

# DRF stuff
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from django.http import HttpResponse
from .serializers import *

class SearchViewDaily(TemplateView):
    template_name = 'search_daily.html'

    def get_queryset(self, **kwargs):
        return LogDaily.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        q = self.request.GET
        context = super(SearchViewDaily, self).get_context_data(**kwargs)
        if q:
            if self.request.user.is_superuser:
                filter = LogFilterDaily(q, queryset=self.get_queryset(**kwargs))
            else:
                #TODO: filter in order to not see other users history
                filter = LogFilterDaily(q, queryset=self.get_queryset(**kwargs))
        else:
            # hack to return 0 objs in the index
            filter = LogFilterDaily(q, queryset=LogDaily.objects.all()[:0])
        filter.form.helper = LogDailyFilterFormHelper()
        table = LogTableDaily(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        return context

class SearchView(TemplateView):
    template_name = 'search.html'

    def get_queryset(self, **kwargs):
        return Log.objects.all()

    def get_context_data(self, **kwargs):
        q = self.request.GET
        context = super(SearchView, self).get_context_data(**kwargs)
        if q:
            filter = LogFilter(q, queryset=self.get_queryset(**kwargs))
        else:
            # hack to return 0 objs in the index
            filter = LogFilter(q, queryset=Log.objects.all()[:0])
        filter.form.helper = LogFilterFormHelper()
        table = LogTable(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        return context

class LogTable(ExportMixin, django_tables2.Table):
    class Meta:
        model = Log
        fields = ('person', 'rfid', 'event', 'date', 'logged_time', 'laser_usage_time')

class LogTableDaily(ExportMixin, django_tables2.Table):
    class Meta:
        model = LogDaily
        fields = ('person', 'rfid', 'date', 'usage_time', 'laser_usage_time')

class LogFilterFormHelper(FormHelper):
    form_method = 'GET'
    #form_show_labels = False
    layout = Layout(
        Row(
            Div('person', css_class='col-sm-4'),
            Div('rfid', css_class='col-sm-4'),
            Div('event', css_class='col-sm-4'),
          ),
        Submit('submit', 'Apply Filter'),
    )

class LogDailyFilterFormHelper(FormHelper):
    form_method = 'GET'
    #form_show_labels = False
    layout = Layout(
        Row(
            Div('person', css_class='col-sm-4'),
            Div('rfid', css_class='col-sm-4'),
          ),
        Submit('submit', 'Apply Filter'),
    )

@api_view(['GET'])
@authentication_classes((TokenAuthentication,)) 
@permission_classes((IsAuthenticated,))
def people_collection(request):
    if request.method == 'GET':
        people = Person.objects.all()
        serializer = PersonSerializer(people, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@authentication_classes((TokenAuthentication,)) 
@permission_classes((IsAuthenticated,))
def person_by_rfid(request, rfid_tag):
    try:
        person = Person.objects.get(rfid_tag__uid=rfid_tag)
    except Person.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PersonSerializer(person)
        return Response(serializer.data)

@api_view(['GET'])
@authentication_classes((TokenAuthentication,)) 
@permission_classes((IsAuthenticated,))
def daily_usage_by_rfid(request, rfid_tag):
    try:
        usage = LogDaily.objects.get(rfid__uid=rfid_tag, date=datetime.datetime.now())
    except LogDaily.DoesNotExist:
        return Response({'laser_usage_time': '00:00:00'})

    if request.method == 'GET':
        serializer = LogDailySerializer(usage)
        return Response(serializer.data)

@api_view(['GET'])
@authentication_classes((TokenAuthentication,)) 
@permission_classes((IsAuthenticated,))
def rfid_auth(request):
    if request.method == 'GET':
        uid = request.GET.get('uid', '')
        resource = request.GET.get('resource', '')
        action = request.GET.get('action', '')
        usage_time = int(request.GET.get('usage_time', 0))

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
                    # send email on each logout:
                    if action == 'LOO':
                        try:
                            log_daily = LogDaily.objects.get(person=log_obj.person, rfid=log_obj.rfid, date=log_obj.date)
                        except LogDaily.DoesNotExist:
                                log_daily = None
                        if log_daily != None:
                            if log_daily.laser_usage_time:
                                send_mail(
                                    'LASER USAGE',
                                    str(log_daily.laser_usage_time),
                                    'eblab@acaia.ca',
                                    ['tvaz@riseup.net'],
                                    fail_silently=True,
                                )
                    if action == 'LAE':
                        last_log = Log.objects.filter(event__event='LAS').latest('date')
                        if log_obj.person == last_log.person:
                            log_obj.laser_usage_time = datetime.timedelta(seconds=usage_time)
                            # Log daily recording:
                            log_daily, created = LogDaily.objects.get_or_create(person=log_obj.person, rfid=log_obj.rfid, date=log_obj.date)
                            if log_daily.laser_usage_time:
                                log_daily.laser_usage_time = log_daily.laser_usage_time + log_obj.laser_usage_time
                            else:
                                log_daily.laser_usage_time = log_obj.laser_usage_time
                            log_daily.save()

                    log_obj.save() 
                        
                    return HttpResponse("Logged", status=200)
            else: # unknown resource
                return HttpResponse(status=406)
        # Tag invalid / not found
        else:
            return HttpResponse(status=406)
