from __future__ import division
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from tagging.models import Tag
from authority.models import Permission
from busylissy import blactivity

from stdimage import StdImageField
from tagging.fields import TagField

import os, datetime

CHOICES = (('1', _(u'On Hold')), ('2', _(u'In Progress')), ('3', _(u'Finished')))
    
def project_dir(instance, filename):
    ext = filename.split('.')[-1]
    return 'projects/%s/logo-%s.%s' % (instance.pk, instance.slug, ext)

class ProjectManager(models.Manager):
    """ Manager for projects """
    def ordered_projects(self, user, status=2):
        """ Return project ordered on priority """
        all_projects = Project.objects.filter(status=status, members=user)

        # retrieve priority
        all_projects = [(project, project.project_value(user)) for project in all_projects]
        # sort on priority
        all_projects = sorted(all_projects, key=lambda x:(x[1], x[0].latest_activity, x[0].name), reverse=True)

        return all_projects

    def create_project_dir(self, sender, instance, *args, **kwargs):
        """ Create a directory for the files """
        if 'created' in kwargs:
            file_path = '%s/%s/%s/' % (settings.MEDIA_ROOT, 'projects/', str(instance.id))
            if not os.path.exists(file_path):
                os.makedirs(file_path)
    
class Project(models.Model):
    name = models.CharField(_(u'name'), max_length=50)
    slug = models.SlugField(_(u'slug'), unique=True)
    description = models.TextField(_(u'description'))
    url = models.URLField(_(u'url'), verify_exists=False, blank=True) 
    image = StdImageField(upload_to=project_dir, blank=True, size=(200, 100, True))
    members = models.ManyToManyField(User, verbose_name=_(u'members'), related_name='project_members')
    date = models.DateField(_(u'date'), auto_now=False, auto_now_add=True)
    status = models.IntegerField(_(u'status'), choices=CHOICES, default=2)
    tags = TagField()

    objects = ProjectManager()
    
    valid_actions = ['started', 'updated', 'invited']

    class Meta:
        verbose_name = _(u'project')
        verbose_name_plural = _(u'projects')

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """
        Delete the file directory when removing a project.
        Delete the tags
        Delete the permissions
        """
        file_path = '%s/%s/%s/' % (settings.MEDIA_ROOT, 'projects/', str(self.pk))
        if os.path.exists(file_path):
            import shutil
            shutil.rmtree(file_path)

        # Delete tags
        Tag.objects.update_tags(self, None)

        # Delete permissions
        permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(self), object_id=self.id)
        permissions.delete()

        super(Project, self).delete(*args, **kwargs)

    def progress_value(self, completed=False):
        """ Progress value """
        from busylissy.bltask.models import Task

        if completed:
            all_nodes = Task.objects.filter(project__slug=self.slug, completed=True)
        else:
            all_nodes = Task.objects.filter(project__slug=self.slug)

        progress_value = 0
        if all_nodes:
            sorted_nodes = sorted(all_nodes, key=lambda x:(x.depth), reverse=True)
            lowest = sorted_nodes[0].depth

            for task in sorted_nodes:
                diff = lowest - task.depth
                progress_value += 2**diff

        return progress_value

    def project_value(self, user):
        """ Give project a value for this user """
        from busylissy.bltask.models import Task
        from busylissy.blmessage.models import Thread

        ctype = ContentType.objects.get_for_model(self)
        thread_count = Thread.objects.filter(content_type__pk=ctype.pk,
                                             object_id=self.pk).exclude(seen_by=user).count()

        task_count = Task.objects.filter(Q(project=self),
                                         Q(completed=False),
                                         Q(assigned_to=None)|Q(assigned_to=user),).count()

        total_value = task_count + thread_count
        
        return total_value

    @property
    def latest_activity(self):
        """ Return latest activity """
        from busylissy.blactivity.models import Activity

        act = Activity.objects.get_activities_for_project(self.slug)
        if act:
            return act[0].time
        else:
            date = datetime.datetime(self.date.year, self.date.month, self.date.day)
            return date

    @property
    def progress(self):
        """ Progress of project """
        total = self.progress_value()
        progress = self.progress_value(completed=True)

        if total > 0:
            return progress/total*100
        else: return 0

blactivity.register(Project)        
post_save.connect(Project.objects.create_project_dir, sender=Project)
        
                
        
