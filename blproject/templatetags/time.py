import datetime
import re
from django import template
from django.utils.translation import ugettext as _

register = template.Library()

def define_pluralize(string, number):
    if number == 1:
        if string == "year":
            return _("year")
        elif string == "week":
            return _("week")
        elif string == "day":
            return _("day")
        elif string == "hour":
            return _("hour")
        elif string == "minute":
            return _("minute")
    else:
        if string == "year":
            return _("years")
        elif string == "week":
            return _("weeks")
        elif string == "day":
            return _("days")
        elif string == "hour":
            return _("hours")
        elif string == "minute":
            return _("minutes")

@register.simple_tag
def humanize_timesince(start_time):
    delta = datetime.datetime.now() - start_time
    
    plural = lambda x: 's' if x != 1 else ''

    num_years = delta.days / 365
    if (num_years > 0):
        return "%d %s" % (num_years, define_pluralize("year", num_years))

    num_weeks = delta.days / 7
    if (num_weeks > 0):
        return "%d %s" % (num_weeks, define_pluralize("week", num_weeks))
        
    if (delta.days > 0):
        return "%d %s" % (delta.days, define_pluralize("day", delta.days))

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
        return "%d %s" % (num_hours, define_pluralize("hour", num_hours))

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
        return "%d %s" % (num_minutes, define_pluralize("minute", num_minutes))

    return _("a few seconds")

@register.simple_tag
def humanize_timeuntil(end_time):
    delta = end_time - datetime.datetime.now().date()

    plural = lambda x: 's' if x != 1 else ''
    
    num_years = delta.days / 365
    if (num_years > 0):
        return "%d %s" % (num_years, define_pluralize("year", num_years))

    num_weeks = delta.days / 7
    if (num_weeks > 0):
        return "%d %s" % (num_weeks, define_pluralize("week", num_weeks))
        
    if (delta.days > 0):
        return "%d %s" % (delta.days, define_pluralize("day", delta.days))

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
        return "%d %s" % (num_hours, define_pluralize("hour", num_hours))

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
        return "%d %s" % (num_minutes, define_pluralize("minute", num_minutes))

    return _("a few seconds")
