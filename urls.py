from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template

import authority
from registration.forms import RegistrationFormUniqueEmail

from busylissy.bltask import views as bltask_views
from busylissy.blproject import views as blproject_views
from busylissy.blinvite import views as blinvite_views
from busylissy.blprofile.models import UserProfile
from busylissy.blmessage import views as blmessage_views
from busylissy.blactivity.feeds import UserFeed, ProjectFeed

admin.autodiscover()
authority.autodiscover()

urlpatterns = patterns('',
    (r'^profiles/', include('busylissy.blprofile.urls')),
    (r'^groups/', include('busylissy.blgroup.urls')),

    #TODO: Monkey-patch, remove after new release of django_authopenid
    url(r'^activate/complete/$',
        direct_to_template,
        {'template': 'registration/activate.html'},
        name='registration_activation_complete'),

    # Our signup form requires an unique e-mail address
    url(r'^account/signup/$',
        'registration.views.register',
        {'backend': 'registration.backends.default.DefaultBackend',
         'form_class':RegistrationFormUniqueEmail},
         name='registration_register'),

    (r'^account/', include('django_authopenid.urls')),
    (r'^agenda/', include('busylissy.blagenda.urls')),
    (r'^projects/', include('busylissy.blproject.urls')),
    (r'^messages/', include('busylissy.blmessage.urls')),
    (r'^language/', include('localeurl.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),

    url(r'^i/(?P<invite_key>\w{40})/(?P<answer>y|n)/$',
        blinvite_views.response,
        name='invite-response-answer'),

    url(r'^i/(?P<invite_key>\w{40})/$',
        blinvite_views.response,
        name='invite-response-positive'),

    url(r'^$',
        blproject_views.index,
        name='busylissy-home'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

)

feeds = {
    'user': UserFeed,
    'project': ProjectFeed,
}

urlpatterns += patterns('',
        (r'^authority/', include('authority.urls')),

        (r'^feeds/(?P<url>.*)/$',
         'django.contrib.syndication.views.feed',
         {'feed_dict': feeds},),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True, }),
)
