import calendar
import itertools
from datetime import datetime, timedelta, time

from django import http
from django.db import models
from django.template.context import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from busylissy.blagenda.models import Event, Occurrence
from busylissy.blagenda import utils, forms
from busylissy.blagenda.forms import EventForm, SingleOccurrenceForm
from busylissy.blagenda.conf import settings as agenda_settings
from busylissy.blproject.models import Project
from busylissy.blactivity.models import Activity

from dateutil import parser

if agenda_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(agenda_settings.CALENDAR_FIRST_WEEKDAY)

@login_required
def event_view(request, pk, project_slug=None, template='blagenda/event_detail.html'):
    '''
    View an ``Event`` instance and optionally update either the event or its
    occurrences.

    Context parameters:

    event
        the event keyed by ``pk``

    event_form
        a form object for updating the event

    recurrence_form
        a form object for adding occurrences
    '''
    event = get_object_or_404(Event, pk=pk)

    if project_slug:
        project = get_object_or_404(Project, slug=project_slug, members=request.user)
    else: project = None

    event_form = EventForm(project, request.user, instance=event)

    occurrence =  event.occurrence_set.all()[0]

    start_time = (occurrence.start_time - datetime.combine(occurrence.start_time.date(), time(0))).seconds

    recurrence_form = SingleOccurrenceForm(event, initial={'day': occurrence.start_time.date(),
                                                           'start_time_delta': start_time, })

    if request.method == 'POST':
        event_form = EventForm(project, request.user, request.POST, instance=event)
        recurrence_form = SingleOccurrenceForm(event, request.POST, instance=occurrence)
        if event_form.is_valid() and recurrence_form.is_valid():
            event = event_form.save(request.user, project)
            recurrence_form.save(event)

            # Notifications
            request.user.message_set.create(message=_("Event '%(event)s' has been updated" % {'event': event.title }))
            event.create_activity(request.user, Activity.UPDATE)

            if project_slug:
                return http.HttpResponseRedirect(reverse('agenda-monthly-view', kwargs = {'project_slug': project_slug, 'month': occurrence.start_time.month , 'year': occurrence.start_time.year }))
            else:
                return http.HttpResponseRedirect(reverse('agenda-monthly-view', kwargs = {'month': occurrence.start_time.month , 'year': occurrence.start_time.year }))

    return render_to_response(
        template,
        dict(project=project, event=event, event_form=event_form, recurrence_form=recurrence_form),
        context_instance=RequestContext(request)
    )

@login_required
def add_event(request, project_slug=None, template='blagenda/add_event.html'):
    '''
    Add a new ``Event`` instance and 1 or more associated ``Occurrence``s.

    Context parameters:

    dtstart
        a datetime.datetime object representing the GET request value if present,
        otherwise None

    event_form
        a form object for updating the event

    recurrence_form
        a form object for adding occurrences

    '''
    dtstart = None
    event = None
    if project_slug:
        project = get_object_or_404(Project, slug=project_slug, members=request.user)
    else:
        project = None

    if request.method == 'POST':
        event_form = EventForm(project, request.user, request.POST)
        recurrence_form = SingleOccurrenceForm(event, request.POST)
        if event_form.is_valid() and recurrence_form.is_valid():
            event = event_form.save(request.user, project)
            occurrence = recurrence_form.save(event)

            # Notifications
            request.user.message_set.create(message=_("Event '%(event)s' has been created" % {'event': event.title }))
            event.create_activity(request.user, Activity.CREATE)

            if project:
                 return http.HttpResponseRedirect(reverse('agenda-monthly-view', kwargs = {'project_slug': project_slug, 'month': occurrence.start_time.month , 'year': occurrence.start_time.year }))
            else:
                return http.HttpResponseRedirect(reverse('agenda-monthly-view', kwargs = {'month': occurrence.start_time.month , 'year': occurrence.start_time.year }))

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except:
                # TODO A badly formatted date is passed to add_event
                dtstart = datetime.now()
        else: dtstart = datetime.now()

        event_form = EventForm(project, request.user)
        start_time = (dtstart - datetime.combine(dtstart.date(), time(0))).seconds

        recurrence_form = SingleOccurrenceForm(event, initial={'day': dtstart.date(),
                                                               'start_time_delta': start_time, })

    return render_to_response(
        template,
        dict(dtstart=dtstart, event_form=event_form, recurrence_form=recurrence_form, project=project),
        context_instance=RequestContext(request)
    )

def _datetime_view(
    request,
    template,
    dt,
    project,
    timeslot_factory=None,
    items=None,
    params=None
):
    '''
    Build a time slot grid representation for the given datetime ``dt``. See
    utils.create_timeslot_table documentation for items and params.

    Context parameters:

    day
        the specified datetime value (dt)

    next_day
        day + 1 day

    prev_day
        day - 1 day

    timeslots
        time slot grid of (time, cells) rows

    '''
    timeslot_factory = timeslot_factory or utils.create_timeslot_table
    params = params or {}
    data = dict(
        project=project,
        day=dt,
        next_day=dt + timedelta(days=+1),
        prev_day=dt + timedelta(days=-1),
        timeslots=timeslot_factory(dt, items, **params),
    )

    return render_to_response(
        template,
        data,
        context_instance=RequestContext(request)
    )

@login_required
def month_view(
    request,
    year,
    month,
    project_slug=None,
    template='blagenda/monthly_view.html',
    queryset=None
):
    '''
    Render a tradional calendar grid view with temporal navigation variables.

    Context parameters:

    today
        the current datetime.datetime value

    calendar
        a list of rows containing (day, items) cells, where day is the day of
        the month integer and items is a (potentially empty) list of occurrence
        for the day

    this_month
        a datetime.datetime representing the first day of the month

    next_month
        this_month + 1 month

    last_month
        this_month - 1 month

    '''
    year, month = int(year), int(month)

    cal = calendar.monthcalendar(year, month)
    dtstart = datetime(year, month, 1)
    last_day = max(cal[-1])
    dtend = datetime(year, month, last_day)

    # TODO Whether to include those occurrences that started in the previous
    # month but end in this month?
    if queryset:
        queryset = queryset._clone()
    else:
        queryset = Occurrence.objects.select_related()

    if project_slug:
        occurrences = queryset.filter(start_time__year=year, start_time__month=month, event__project__slug=project_slug)
        project = get_object_or_404(Project, slug=project_slug, members=request.user)
    else:
        projects = Project.objects.filter(members=request.user)
        occurrences = queryset.filter(start_time__year=year, start_time__month=month, event__project__in=projects)
        template = 'blagenda/user/monthly_view.html'
        projects = filter(lambda p: p in [(item.event.project) for item in queryset.filter(event__project__in=projects)], projects)

    by_day = dict([
        (dom, list(items))
        for dom,items in itertools.groupby(occurrences, lambda o: o.start_time.day)
    ])

    data = dict(
        today=datetime.now(),
        calendar=[[(d, by_day.get(d, [])) for d in row] for row in cal],
        this_month=dtstart,
        next_month=dtstart + timedelta(days=+last_day),
        last_month=dtstart + timedelta(days=-1),
    )

    if project_slug:
        data['project'] = project
    else:
        data['projects'] = projects

    return render_to_response(
        template,
        data,
        context_instance=RequestContext(request)
    )

@login_required
def index(request, project_slug=None):
    """
    Index page for the agenda on default
    display in month-view the current month
    """
    year = datetime.now().year
    month = datetime.now().month

    return month_view(request, year, month, project_slug)

@login_required
def delete_event(request, event_id, project_slug=None):
    """ Delete the event """
    event = get_object_or_404(Event, pk=event_id)

    if request.user in event.project.members.all():
        event.create_activity(request.user, Activity.DELETE)
        event.delete()

        # Notifications
        request.user.message_set.create(message=_("Event '%(event)s' has been deleted" % {'event': event.title }))

        if project_slug:
            return http.HttpResponseRedirect(reverse('agenda-index', kwargs={'project_slug': project_slug }))
        else:
            return http.HttpResponseRedirect(reverse('agenda-index'))
    else:
        raise http.Http404

def week_cal(request, project_slug):
    """ Week calendar for dashboard """

    year, month = datetime.now().year, datetime.now().month

    occurrences = Occurrence.objects.select_related().filter(start_time__year=year, start_time__month=month, event__project__slug=project_slug)
    project = get_object_or_404(Project, slug=project_slug)

    by_day = dict([
        (dom, list(items))
        for dom,items in itertools.groupby(occurrences, lambda o: o.start_time.day)
    ])

    today = datetime.now().date()
    end_of_week = today + timedelta(days=7)

    days = []
    day = today
    while day <= end_of_week:
        days.append(day)
        day += timedelta(days=1)

    data = dict(
        today=datetime.now(),
        project=project,
        calendar=[(d, by_day.get(d.day, [])) for d in days],
        this_month=datetime.now(),
    )

    template = 'blagenda/week_cal.html'

    return render_to_response(
        template,
        data,
        context_instance=RequestContext(request)
    )
