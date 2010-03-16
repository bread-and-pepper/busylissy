from django.conf.urls.defaults import *

from busylissy.blinvite.views import *

urlpatterns = patterns('',
    url('^$',
        index,
        name='invite-index'),
)
