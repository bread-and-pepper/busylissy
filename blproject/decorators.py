from django.utils.functional import wraps
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.utils.http import urlquote
from django.http import HttpResponseRedirect

from busylizzy.blproject.models import Project

def get_project_from_slug(view):
    """
    Checks if a user is a member of a project. Already fetches the project in
    the view.

    """
    def wrapper(request, project, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                project = Project.objects.get(slug__iexact=project, members=request.user)
            except Project.DoesNotExist:
                raise Http404
            else:
                request.project = project # Add project to all templates.
                return view(request, project=request.project, *args, **kwargs)
        else:
            path = urlquote(request.get_full_path())
            tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
    return wraps(view)(wrapper)

def edit_permission(view):
    """
    Check if a user has permissions to edit or the view is accessible for logged in users
    """
    def wrapper(request, project=None, *args, **kwargs):
        if request.user.is_authenticated():
            if project:
                try:
                    project = Project.objects.get(slug__iexact=project, members=request.user)
                except Project.DoesNotExist:
                    raise Http404
                else:
                    request.project = project
            else:
                request.project = None
            return view(request, project=request.project, *args, **kwargs)
        else:
            path = urlquote(request.get_full_path())
            tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
    return wraps(view)(wrapper)
