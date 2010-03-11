from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template

import authority
from registration.forms import RegistrationFormUniqueEmail

from busylizzy.bltask import views as bltask_views
from busylizzy.blproject import views as blproject_views
from busylizzy.blinvite import views as blinvite_views
from busylizzy.blprofile.models import UserProfile
from busylizzy.blmessage import views as blmessage_views
from busylizzy.blactivity.feeds import UserFeed, ProjectFeed

admin.autodiscover()
authority.autodiscover()

urlpatterns = patterns('',
    (r'^profiles/', include('busylizzy.blprofile.urls')),
    (r'^groups/', include('busylizzy.blgroup.urls')),

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
    (r'^agenda/', include('busylizzy.blagenda.urls')),
    (r'^projects/', include('busylizzy.blproject.urls')),
    (r'^messages/', include('busylizzy.blmessage.urls')),
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
        name='busylizzy-home'),

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
