import authority
from authority.permissions import BasePermission

from busylizzy.blproject.models import Project

class ProjectPermission(BasePermission):
    label = 'project_permission'

authority.register(Project, ProjectPermission)
