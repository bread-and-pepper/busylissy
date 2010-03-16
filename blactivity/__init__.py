from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

__all__ = ('register',)

class AlreadyRegistered(Exception):
    """ An attempt was made to register a model to activity more than once """
    pass

registry = []

def create_activity(self, actor, action, indirect_object=None):
    """
    This method is added to the each model which is registered
    to Activities.

    """
    from busylissy.blactivity.models import Activity

    if self._meta.module_name == "thread":
        project = self.content_type.get_object_for_this_type(pk=self.object_id)
    elif self._meta.module_name == "message":
        project = self.thread.content_type.get_object_for_this_type(pk=self.thread.object_id)
    elif self._meta.module_name == "project":
        project = self
    else:
        project = self.project

    activity = Activity(
        actor=actor,
        action=action,
        project=project,
        content_object=self,
        )

    if indirect_object:
        activity.indirect_content_object = indirect_object

    activity.save()
    
    return activity

def register(model):
    """ Registers extra functionality to a model """
    if model in registry:
        raise AlreadyRegistered(
            _('The model %s has already been registered.') % model.__name__)
    registry.append(model)
    
    # add method to model
    setattr(model, 'create_activity', create_activity)
