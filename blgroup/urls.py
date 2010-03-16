from django.conf.urls.defaults import *

from busylissy.blgroup import views as blgroup_views
from busylissy.blprofile import views as blprofile_views
from busylissy.blmessage import views as blmessage_views

urlpatterns = patterns('',
        url(r'^add/$',
            blgroup_views.add_edit,
            name='group-add'),

        url(r'^tags/(?P<tags>[-+\w]*)$',
            blgroup_views.tagged_groups,
            name='group-tag'),

        url(r'^(?P<slug>[-\w]+)/edit/$',
            blgroup_views.add_edit,
            name='group-edit'),

        url(r'^(?P<slug>[-\w]+)/delete/$',
            blgroup_views.delete,
            name='group-delete'),

        url(r'^(?P<slug>[-\w]+)/project/add/$',
            blgroup_views.start_project,
            name='group-start-project'),
                       
        # Messages
        url(r'^(?P<object_slug>[-\w]+)/messages/$',
            blmessage_views.list_for_model,
            {'model': 'blgroup.group',
             'template': 'blgroup/messages/list.html'},
            name='group-messages'),

        url(r'^(?P<object_slug>[-\w]+)/messages/add/$',
            blmessage_views.add_edit_thread,
            {'model': 'blgroup.group',
             'template': 'blgroup/messages/form_thread.html'},
            name='group-thread-add',),

        url(r'^(?P<object_slug>[-\w]+)/messages/tags/(?P<tags>[-+\w]*)$',
            blmessage_views.tags_for_model,
            {'model': 'blgroup.group'},
            name='group-thread-tag',),

        url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/$',
            blmessage_views.detail_for_model,
            {'model': 'blgroup.group',
             'template': 'blgroup/messages/detail.html'},
            name='group-thread-detail',),

        url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/edit/$',
            blmessage_views.add_edit_thread,
            {'model': 'blgroup.group',
             'template': 'blgroup/messages/form_thread.html'},
            name='group-thread-edit',),

        url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/delete/$',
            blmessage_views.delete_thread_for_model,
            {'model': 'blgroup.group'},
            name='group-thread-delete',),

        url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/post/(?P<message_id>\d+)/delete/$',
            blmessage_views.delete_message_for_model,
            {'model': 'blgroup.group'},
            name='group-message-delete'),

        url(r'^(?P<object_slug>[-\w]+)/messages/(?P<thread_id>\d+)/post/(?P<message_id>\d+)/edit/$',
            blmessage_views.edit_message_for_model,
            {'model': 'blgroup.group'},
            name='group-message-edit'),

        # Members
        url(r'^(?P<model_slug>[-\w]+)/members/add/$',
            blprofile_views.add_member,
            {'model': 'blgroup.group',
             'template': 'blgroup/member_form.html'},
            name='group-member-add'),

        url(r'^(?P<model_slug>[-\w]+)/members/(?P<member_slug>[-\w]+)/delete/$',
            blprofile_views.delete_member,
            {'model': 'blgroup.group'},
            name='group-member-delete'),

        url(r'^(?P<model_slug>[-\w]+)/members/(?P<member_slug>[-\w]+)/admin/$',
            blprofile_views.make_admin,
            {'model': 'blgroup.group'},
            name='group-member-admin'),

        url(r'^(?P<slug>[-\w]+)/$',
            blgroup_views.detail,
            name='group-detail',),

        url(r'^$',
            blgroup_views.list,
            name='group-list'),
)
