from django.conf.urls.defaults import *

from busylizzy.blagenda import views

urlpatterns = patterns('',
    url(r'^$',
        views.index,
        name='agenda-index'),

    url(r'^calendar/(?P<year>\d{4})/(?P<month>0?[1-9]|1[012])/$',
        views.month_view,
        name='agenda-monthly-view'),

    url(r'^events/add/$',
        views.add_event,
        name='agenda-add-event'),

    url(r'^events/add/remote/$',
        views.add_event,
        {'template': 'blagenda/includes/add_event.html'},
        name='agenda-add-remote-event'),

    url(r'^events/(\d+)/delete/$',
        views.delete_event,
        name='agenda-delete-event'),

    url(r'^events/(\d+)/remote/$',
        views.event_view,
        {'template': 'blagenda/includes/event_detail.html'},
        name='agenda-edit-remote-event'),

    url(r'^events/(\d+)/$',
        views.event_view,
        name='agenda-event'),

    url(r'^week/$',
        views.week_cal,
        name='week-cal'),

)
