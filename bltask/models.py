from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

from busylissy.blproject.models import Project
from busylissy import blactivity
from busylissy.blagenda.models import create_event, EventType, Event

from treebeard.mp_tree import MP_Node
import tagging

class TaskManager(models.Manager):
    """ Manage some common tasks """
    def _check_depth(self, depth):
        try: depth = int(depth)
        except: depth = None
        return depth

    def get_nodes_for_project(self, project, depth=None):
        """ Returns the nodes for a project with a depth of ``depth`` """
        # Check for a valid depth
        depth = self._check_depth(depth)

        all_nodes = Task.objects.select_related('assigned_to', 'created_by', 'project').filter(project=project)
        if depth: all_nodes = all_nodes.filter(depth__lte=depth)
        
        all_nodes = [(node, node.get_children_count()) for node in all_nodes]
        return all_nodes

    def task_is_event(self, sender, instance, *args, **kwargs):
        """ If task has due date insert in agenda """
        try:
            event = Event.objects.filter(project=instance.project,
                                         content_type=ContentType.objects.get_for_model(Task),
                                         object_id=instance.pk).delete()
        except:
            pass

        if instance.assigned_to:
            event_user = instance.assigned_to
        else: event_user = instance.created_by

        if instance.due_date:
            create_event(instance.name,
                         EventType.objects.get(label='task'),
                         instance.project,
                         event_user,
                         start_time=instance.due_date,
                         object_id=instance.pk)
            
        return instance

class Task(MP_Node):    
    """ A task item """
    name = models.CharField(_(u'name'), max_length=255)
    note = models.TextField(_(u'note'), blank=True)
    completed = models.BooleanField(_(u'completed'))
    completed_date = models.DateField(_(u'completed date'), null=True, blank=True)
    created_at = models.DateTimeField()
    due_date = models.DateField(_(u'due date'), null=True, blank=True)
    tags = tagging.fields.TagField(blank=True)

    my_objects = TaskManager()
    
    # Foreignkeys
    assigned_to = models.ForeignKey(User,
                                    null=True,
                                    blank=True,
                                    related_name='assigned_tasks',
                                    limit_choices_to={'project_members__slug': 'self.tasks.slug'},
                                    verbose_name=_(u'assigned to'))
    
    created_by = models.ForeignKey(User,
                                   related_name='created_tasks',
                                   verbose_name=_(u'created by'))
    
    project = models.ForeignKey(Project,
                                related_name='tasks',
                                verbose_name=_(u'project'))


    valid_actions = ['created', 'updated', 'deleted', 'closed']
    
    def __unicode__(self):
        return '%s' % self.name

    def toggle(self):
        # Move the task correctly
        completed = not self.completed
        
        # Change itself
        self.completed = completed
        self.save()
        
        # Trickle down
        for d in self.get_descendants():
            d.completed = completed
            d.save()

        # If it's a leaf check what the consequences are above
        ancestors = self.get_ancestors()
        if len(ancestors) > 0:
            if not completed:
                for a in ancestors:
                    a.completed = completed
                    a.save()
            else:
                for a in ancestors.reverse():
                    if len(a.get_children().filter(completed=False)) == 0:
                        a.completed = True
                        a.save()
        return True

blactivity.register(Task)
post_save.connect(Task.my_objects.task_is_event, sender=Task)
