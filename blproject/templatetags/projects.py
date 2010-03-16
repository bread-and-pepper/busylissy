from django import template
from django.db import models
from busylissy.blproject.models import Project

import datetime
import re

register = template.Library()

@register.simple_tag
def count_projects(user, status='active'):
    choices = {'finished': '3', 'active': '2', 'hold': '1'}

    projects_total = Project.objects.filter(members=user, status=choices[status]).count()

    return projects_total

@register.simple_tag
def project_progress(project_slug, type=None):
    """ Return progress of project """
    project = Project.objects.get(slug=project_slug)
    progres = int(round(project.progress))
    
    if progres == 0 and type == "string":
        progres = ""
    else:
        progres = str(progres) + "%"
    
    return progres
        
