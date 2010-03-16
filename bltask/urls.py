from django.conf.urls.defaults import *

from busylissy.bltask import views as bltask_views

urlpatterns = patterns('',
    url(r'^(?P<parent>\d+)/add/$',
        bltask_views.add_edit,
        name='task-add'),

    url(r'^(?P<instance>\d+)/edit/$',
        bltask_views.add_edit,
        name='task-edit'),
    
    url(r'^(?P<id>\d+)/move/(?P<parent>[\d]+)/$',
        bltask_views.move,
        name='task-move'),

    url(r'^(?P<id>\d+)/toggle/$',
        bltask_views.toggle,
        name='task-toggle'),

    url(r'^(?P<id>\d+)/delete/$',
        bltask_views.delete,
        name='task-delete'),

    url(r'^tags/(?P<tags>[-+\w]*)$',
        bltask_views.tagged_tasks,
        name='task-tag'),

    url(r'^calendar/(?P<direction>forw|back)/(?P<today>[-\d]*)$',
        bltask_views.week_cal,
        name='milestone-calendar'),

    url(r'^add/$',
        bltask_views.add_edit,
        name='task-add-list'),

    url(r'^$',
        bltask_views.task_project_list,
        name='task-list'),
)
