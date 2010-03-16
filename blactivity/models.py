from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template import loader, Context
from django.core.mail import send_mass_mail, EmailMessage

from busylissy.blproject.models import Project

class ActivityManager(models.Manager):
    """ Manager for retrieving activities """
    def get_activities_for_project(self, project_slug, limit=None):
        """ Return the latest activities for a project """
        return self.filter(project__slug=project_slug)

class Activity(models.Model):
    """ Saving an activity """
    CREATE = 1
    UPDATE = 2
    DELETE = 3
    CLOSE = 4
    COMMENT = 5
    INVITE = 6
    START = 7
    ADMIN = 8
    JOIN = 9

    ACTION_CHOICES = (
        (CREATE, _('created')),
        (UPDATE, _('updated')),
        (DELETE, _('deleted')),
        (CLOSE, _('closed')),
        (COMMENT, _('commented on')),
        (INVITE, _('invited')),
        (START, _('started')),
        (ADMIN, _('permissions')),
        (JOIN, _('joined')),
    )

    actor = models.ForeignKey(User, related_name='activities')
    action = models.SmallIntegerField(_('action'), choices=ACTION_CHOICES)
    project = models.ForeignKey(Project, related_name='activities')
    time = models.DateTimeField(_('time'), auto_now_add=True)

    # Direct object
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='activity_objects')
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Indirect object
    indirect_object_id = models.PositiveIntegerField(blank=True, null=True)
    indirect_content_type = models.ForeignKey(ContentType, related_name='activity_indirect_objects', blank=True, null=True)
    indirect_content_object = generic.GenericForeignKey('indirect_content_type', 'indirect_object_id')

    objects = ActivityManager()

    def __unicode__(self):
        return self.humanize(admin=True).strip()

    def save(self, *args, **kwargs):
        """
        When saving an activity e-mail notification to project members
        """
        super(Activity, self).save(*args, **kwargs)

        # Send mail as notification
        if settings.EMAIL_NOTIFICATIONS is True:
            mail_data = self.prepare_mail()
            mail_data.send()
    
    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        ordering = ['-time']
    
    @property
    def app_label(self):
        """ 
        Returns the ``app_label`` so we can search for the templates.
        
        """
        return self.content_type.app_label

    def _get_template_for_action(self, mail=''):
        """ Returns the template for this action """
        options = ['%(app_label)s/actions/%(action)s%(mail)s.txt' % {'app_label': self.app_label,
                                                                     'action': self.get_action_display().replace(' ',''),
                                                                     'mail': mail,
                                                                     },
                   '%(app_label)s/actions/generic%(mail)s.txt' % {'app_label': self.app_label,
                                                                  'mail': mail },
                   'blactivity/generic.txt']
        t = loader.select_template(options)
        return t

    def humanize(self, admin=False, mail=False):
        """ Returns a sentence of the committed action """
        if admin:
            template = loader.get_template('blactivity/admin.txt')
        elif mail:
            template = self._get_template_for_action('_mail')
        else:
            template = self._get_template_for_action()

        context = Context(
            {'actor': self.actor.username,
             'actor_id': self.actor.id,
             'action': self.get_action_display(),
             'project': self.project,
             'project_id': self.project.id,
             'time': self.time,
             'object': self.content_object,
             'object_id': self.object_id,
             'object_type': self.content_type,
             'indirect_object': self.indirect_content_object if self.indirect_object_id else None,
             'indirect_object_id': self.indirect_object_id if self.indirect_object_id else None,
             'MEDIA_URL': settings.MEDIA_URL,
            })
        sentence = template.render(context)
        return sentence

    def prepare_mail(self):
        """ Prepare mass mail """
        subject = "[%(project)s] New activity" % {'project': self.project }
        message = self.humanize(mail=True)
        from_email = settings.EMAIL_HOST_USER
        
        email = EmailMessage(subject, message, from_email, self.recipient_list())
        email.content_subtype = "html"

        return email

    def recipient_list(self):
        """ Return list with all recipient for mail """
        recipient_list = []
        for member in self.project.members.all():
            try:
                profile = member.get_profile()
            except:
                pass
            else:
                if profile.notifications:
                    recipient_list.append(member.email)

        if len(recipient_list) > 0:
            return recipient_list
        else: return None
