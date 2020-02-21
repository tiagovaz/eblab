from django.http import HttpResponse
from eblab.models import RFIDTag, Log, Person, Event
from django.views.generic import TemplateView
from .filters import LogFilter
from django_tables2 import RequestConfig

from django_tables2.export.views import ExportMixin
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div
import django_tables2
import datetime

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
        table_daily = LogTableDaily(filter.qs)
        RequestConfig(self.request, paginate={'per_page': 50}).configure(table)
        context['filter'] = filter
        context['table'] = table
        context['table_daily'] = table_daily
        return context

class LogTable(ExportMixin, django_tables2.Table):
    def render_logged_time(self, value, record):
        return str(value)

    def render_laser_usage_time(self, value, record):
        return str(value)

    class Meta:
        model = Log
        fields = ('id', 'person', 'rfid', 'event', 'date', 'logged_time', 'laser_usage_time')

class LogTableDaily(ExportMixin, django_tables2.Table):
    def render_logged_time(self, value, record):
        return str(value)

    def render_laser_usage_time(self, value, record):
        return str(value)

    class Meta:
        model = Log
        fields = ('logged_time', 'laser_usage_time')

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


def rfid_auth(request):
    if request.method == 'GET':
        uid = request.GET.get('uid', '')
        resource = request.GET.get('resource', '')
        action = request.GET.get('action', '')

        # If the RFID tag is in the database
        if RFIDTag.objects.filter(uid=uid).exists():
            rfidtag_obj = RFIDTag.objects.get(uid=uid)
            event_obj = Log.objects.get(event=action)

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
