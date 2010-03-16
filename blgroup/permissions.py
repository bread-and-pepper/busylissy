import authority
from authority.permissions import BasePermission
from busylissy.blgroup.models import Group

class GroupPermission(BasePermission):
    label = 'group_permission'

authority.register(Group, GroupPermission)
