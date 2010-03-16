from django.conf.urls.defaults import *

from busylissy.blproject import views as blproject_views
from busylissy.blprofile import views as blprofile_views
from busylissy.blmessage import views as blmessage_views

urlpatterns = patterns('',
    url(r'^add/$',
        blproject_views.add_edit,
        name='project-add'),

    url(r'^(active|hold|finished)/$',
        blproject_views.list_by_status,
        name='project-status'),

    url(r'^tags/(?P<tags>[-+\w]*)$',
        blproject_views.tagged_projects,
        name='project-tag'),

    url(r'^(?P<slug>[-\w]+)/edit/$',
        blproject_views.add_edit,
        name='project-edit'),

    url(r'^(?P<slug>[-\w]+)/delete/$',
        blproject_views.delete,
        name='project-delete'),
    
    # Messages
    url(r'^(?P<object_slug>[-\w]+)/messages/$',
        blmessage_views.list_for_model,
        {'model': 'blproject.project'},
        name='project-messages'),

    url(r'^(?P<object_slug>[-\w]+)/messages/add/$',
        blmessage_views.add_edit_thread,
        {'model': 'blproject.project'},
        name='project-thread-add',),

    url(r'^(?P<object_slug>[-\w]+)/messages/tags/(?P<tags>[-+\w]*)$',
        blmessage_views.tags_for_model,
        {'model': 'blproject.project'},
        name='project-thread-tag',),
    
    url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/$',
        blmessage_views.detail_for_model,
        {'model': 'blproject.project'},
        name='project-thread-detail',),

    url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/edit/$',
        blmessage_views.add_edit_thread,
        {'model': 'blproject.project'},
        name='project-thread-edit',),

    url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/delete/$',
        blmessage_views.delete_thread_for_model,
        {'model': 'blproject.project'},
        name='project-thread-delete',),

    url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/post/(?P<message_id>\d+)/delete/$',
        blmessage_views.delete_message_for_model,
        {'model': 'blproject.project'},
        name='project-message-delete'),

    url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/post/(?P<message_id>\d+)/edit/$',
        blmessage_views.edit_message_for_model,
        {'model': 'blproject.project'},
        name='project-message-edit'),

    # Invite application
    (r'^(?P<project_slug>[-\w]+)/invite/', include('busylissy.blinvite.urls')),

    # Agenda application
    (r'^(?P<project_slug>[-\w]+)/agenda/', include('busylissy.blagenda.urls')),                       
                       
    # Members
    url(r'^(?P<model_slug>[-\w]+)/members/(?P<member_slug>[-\w]+)/delete/$',
        blprofile_views.delete_member,
        {'model': 'blproject.project'},
        name='project-member-delete'),
                       
    url(r'^(?P<model_slug>[-\w]+)/members/(?P<member_slug>[-\w]+)/admin/$',
        blprofile_views.make_admin,
        {'model': 'blproject.project'},
        name='project-member-admin'),

    (r'^(?P<project_slug>[-\w]+)/tasks/', include('busylissy.bltask.urls')),
    (r'^(?P<project_slug>[-\w]+)/files/', include('busylissy.blfile.urls')),

    # Activities
    url(r'^(?P<slug>[-\w]+)/activities/(?P<type>[-\w]+)/$',
        blproject_views.detail,
        name='project-activities'),

    url(r'^(?P<slug>[-\w]+)/tags/(?P<tags>[-+\w]*)$',
        blproject_views.tagged_items,
        name='project-tagged-items'),
                       
    url(r'^(?P<slug>[-\w]+)/$',
        blproject_views.detail,
        name='project-detail'),
    
    url(r'^$',
        blproject_views.list,
        name='project-list'),
)
