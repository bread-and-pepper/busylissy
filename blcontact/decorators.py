from django.utils.functional import wraps
from django.http import Http404

from busylizzy.blproject.models import Project

def get_contact(view):
    """
    Checks if user is allowed to see the contacts
    """
    def wrapper(request, project=None, company=None, *args, **kwargs):
        if project:
            try:
                project = Project.objects.get(slug__iexact=project, members=request.user)
            except Project.DoesNotExist:
                raise Http404
            return view(request, project=project, company=None, *args, **kwargs)
        else:
            #try:
            #    company = Company.objects.get(slug__iexact=company, members=request.user)
            #except Company.DoesNotExist:
            raise Http404
            return view(request, project=None, company=None, *args, **kwargs)
    return wraps(view)(wrapper)
                
