from django.conf.urls.defaults import *

from busylizzy.blprofile import views as profile_views

urlpatterns = patterns('',
    # List
    url(r'^$',
        profile_views.list,
        name='profile-list'),

    # Settings
    url(r'^settings/$',
        profile_views.settings,
        name='profile-settings'),
                       
    # Edit
    url(r'^edit/$',
        profile_views.edit,
        name='profile-edit'),
                       
    # Delete
    url(r'^delete/$',
        profile_views.delete,
        name='profile-delete'),
 
    # View your own profile
    url(r'^view/$',
        profile_views.view,
        name='profile-view'),

    # Detail
    url(r'^(?P<username>[-\w]+)/$',
        profile_views.detail,
        name='profile-detail'),
)
