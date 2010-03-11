import authority
from authority.permissions import BasePermission
from busylizzy.blgroup.models import Group

class GroupPermission(BasePermission):
    label = 'group_permission'

authority.register(Group, GroupPermission)
