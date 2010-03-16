from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from busylissy.blcontact import views as blcontact_views

urlpatterns = patterns('',
    url(r'^add/$',
        blcontact_views.add_edit,
        name='contact-add'),

    url(r'^tags/(?P<tags>[-+\w]*)$',
        blcontact_views.tagged_contacts,
        name='contact-tag'),

    url(r'^(?P<id>\d+)/delete/$',
        blcontact_views.delete,
        name='contact-delete'),
                       
    url(r'^(?P<id>\d+)/edit/$',
        blcontact_views.add_edit,
        name='contact-edit'),
                       
    url(r'^(?P<id>\d+)/$',
        blcontact_views.detail,
        name='contact-detail'),
   
    url(r'^(?P<model>[-\w]+)/(?P<slug>[-\w]+)/$',
        blcontact_views.list,
        name='contact-list-model',),

    url(r'^(?P<model>[-\w]+)/$',
        blcontact_views.list,
        name='contact-list-model',),
    
    url(r'^$',
        blcontact_views.list,
        name='contact-list'),
)
