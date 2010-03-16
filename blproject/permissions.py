import authority
from authority.permissions import BasePermission

from busylissy.blproject.models import Project

class ProjectPermission(BasePermission):
    label = 'project_permission'

authority.register(Project, ProjectPermission)
