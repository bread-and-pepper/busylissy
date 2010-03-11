from django.conf.urls.defaults import *

from busylizzy.blinvite.views import *

urlpatterns = patterns('',
    url('^$',
        index,
        name='invite-index'),
)
