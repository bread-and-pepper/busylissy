from django import template
from django.db import models
from django.db.models import Q
from django.conf import settings
from busylizzy.bltask.models import Task
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from busylizzy.blagenda.models import Occurrence
from busylizzy.blproject.models import Project

import datetime, re, itertools

register = template.Library()

def week_cal(project):
    """ Week calendar for dashboard """

    year, month = datetime.datetime.now().year, datetime.datetime.now().month

    occurrences = Occurrence.objects.select_related().filter(start_time__year=year, start_time__month=month, event__project__slug=project.slug)
    project = get_object_or_404(Project, pk=project.pk)
    
    by_day = dict([
        (dom, list(items)) 
        for dom,items in itertools.groupby(occurrences, lambda o: o.start_time.day)
    ])

    today = datetime.datetime.now().date()
    end_of_week = today + datetime.timedelta(days=7)

    days = []
    day = today
    while day <= end_of_week:
        days.append(day)
        day += datetime.timedelta(days=1)

    data = dict(
        today=datetime.datetime.now(),
        project=project,
        calendar=[(d, by_day.get(d.day, [])) for d in days],
        MEDIA_URL=settings.MEDIA_URL,
        this_month=datetime.datetime.now(),
    )

    return data

register.inclusion_tag('blagenda/week_cal.html')(week_cal)

@register.simple_tag
def your_tasks(project, user):
    tasks_total = Task.objects.filter(Q(project=project),
                                      Q(completed=False),
                                      Q(assigned_to=None)|Q(assigned_to=user),).count()

    return tasks_total

@register.simple_tag
def next_milestone(project):
    milestone = Task.objects.filter(project=project).order_by("-due_date")[:1]
    today = datetime.datetime.now()

    due_date = None
    if milestone:
        due_date = milestone[0].due_date

    if due_date and due_date.date() > today.date():
        time_left = -1*(today.date() - due_date.date())
        return str(time_left.days) + _(" days left")
    elif due_date and due_date.date() < today.date():
        time_late = (today.date() - due_date.date())
        return str(time_late.days) + _(" days late")
    else:
        return _("no milestones")
