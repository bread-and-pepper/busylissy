from django.conf.urls.defaults import *

from busylizzy.blfile import views as blfile_views

urlpatterns = patterns('',
   url(r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/upload/$',
       blfile_views.upload,
       name='file-folder-upload'),

   url(r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/mkdir/$',
       blfile_views.mkdir,
       name='file-folder-mkdir'),

   url(r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/delete/$',
       blfile_views.delete,
       name='file-folder-delete'),

   url(r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/rename/(?P<file_name>[_a-zA-Z0-9.-]+)/$',
       blfile_views.rename,
       name='file-folder-rename'),

   url(r'^mkdir/$',
       blfile_views.mkdir,
       name='file-mkdir'),

   url(r'^upload/$',
       blfile_views.upload,
       name='file-upload'),

   url(r'^rename/(?P<file_name>[_a-zA-Z0-9.-]+)/$',
       blfile_views.rename,
       name='file-rename'),
                       
   url(r'^delete/$',
       blfile_views.delete,
       name='file-delete'),
                       
   url(r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/$',
       blfile_views.list,
       name='file-folder-list'),
                       
   url(r'^$',
       blfile_views.list,
       name='file-list'),
)                       

