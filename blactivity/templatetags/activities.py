from django import template
from django.db import models
from busylizzy.blactivity.models import Activity

import re

register = template.Library()

class LatestActivitiesProject(template.Node):
    def __init__(self, project_slug, limit, var_name):
        self.project_slug = template.Variable(project_slug)
        self.limit = limit
        self.var_name = var_name
        
    def render(self, context):
        project_slug = self.project_slug.resolve(context)
        item_list = Activity.objects.get_activities_for_project(project_slug)[:self.limit]
        if item_list and (int(self.limit) == 1):
            context[self.var_name] = item_list[0]
        else:
            context[self.var_name] = item_list
        return ''

@register.tag
def get_latest_activities_project(parser, token):
    """
    Gets any number of latest activities for a project and stores them in a variable

    Syntax::

        {% get_latest_activities_project [project_slug] [limit] as [var_name] %}

    Example usage::

        {% get_latest_activities_project busy_lizzy 10 as latest_activity_list %}
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError, "get_latest tag takes exactly four arguments, not %d" % len(bits)
    if bits[3] != 'as':
        raise template.TemplateSyntaxError, "third argument to get_latest tag must be 'as'"
    return LatestActivitiesProject(bits[1], bits[2], bits[4])
