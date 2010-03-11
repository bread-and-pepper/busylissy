import datetime
from django import template
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def view_by_month(project_slug, year=None, month=None):
    """ Return the correct link for view by month """
    if not year:
        year = datetime.datetime.now().year
        
    if year == datetime.datetime.now().year and not month:
        month = datetime.datetime.now().month
    else: month = '1'
    
    return reverse('agenda-monthly-view', kwargs={'project_slug': project_slug,
                                                  'year': year,
                                                  'month': month})

@register.simple_tag
def view_by_year(project_slug, year=None):
    """ Return the correct link for view by year """
    if not year:
        year = datetime.datetime.now().year

    return reverse('agenda-yearly-view', kwargs={'project_slug': project_slug,
                                                  'year': year})

                                

    
