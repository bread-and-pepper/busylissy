from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from busylizzy.blmessage import views as blmessage_views

urlpatterns = patterns('',
    url(r'^tags/(?P<tags>[-+\w]*)$',
        blmessage_views.tagged_threads,
        name='message-tag'),

    url(r'^(?P<thread_id>\d+)/$',
        blmessage_views.detail,
        name='message-detail'),

    url(r'^(?P<thread_id>\d+)/edit/$',
        blmessage_views.edit_thread,
        name='message-edit'),
                       
    url(r'^(?P<thread_id>\d+)/delete/$',
        blmessage_views.delete_thread,
        name='message-delete'),

    url(r'^(?P<thread_id>\d+)/post/(?P<message_id>\d+)/edit/$',
        blmessage_views.edit_message,
        name='message-post-edit'),
                       
    url(r'^(?P<thread_id>\d+)/post/(?P<message_id>\d+)/delete/$',
        blmessage_views.delete_message,
        name='message-post-delete'),
   
    url(r'^$',
        blmessage_views.list,
        name='message-list'),
)
