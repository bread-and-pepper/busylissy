from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.hashcompat import md5_constructor

from busylizzy.blproject.models import Project
from busylizzy.blactivity.models import Activity

class UserFeed(Feed):
    title = "Busylissy activity feed"
    link = "/projects/"
    copyright = 'Copyright (c) 2009, BusyLissy'
    
    def get_object(self, bits):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(bits) != 2:
            raise ObjectDoesNotExist
        else:
            user = get_object_or_404(User, username=bits[0])

            salt = 'bltoken'
            hash_obj = md5_constructor(str(user.username) + salt + str(user.pk))
            if bits[1] != hash_obj.hexdigest():
                raise Object.DoesNotExist
        return user

    def item_link(self, obj):
        return "/projects/%s/" % obj.project.slug

    def item_pubdate(self, obj):
        return obj.time
    
    def description(self, obj):
        return "Acitvity for busylissy"

    def items(self, obj):
        projects = Project.objects.filter(members=obj)
        return Activity.objects.filter(project__in=projects)[:10]

class ProjectFeed(Feed):
    link = "/projects/" 
    copyright = 'Copyright (c) 2009, BusyLissy'

    def get_object(self, bits):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(bits) != 2:
            raise ObjectDoesNotExist
        else:
            project = get_object_or_404(Project, slug=bits[0])
            
            salt = 'bltoken'
            hash_obj = md5_constructor(str(project.slug) + salt + str(project.pk))
            
        return project

    def title(self, obj):
        return "%s activity feed" % obj.name
    
    def item_link(self, obj):
        return "/projects/%s/" % obj.project.slug

    def item_pubdate(self, obj):
        return obj.time

    def description(self, obj):
        return "Activity for %s" % obj.name
    
    def items(self, obj):
        return Activity.objects.filter(project=obj)[:10]
