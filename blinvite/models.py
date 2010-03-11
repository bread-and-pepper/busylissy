from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from registration.signals import user_registered
from django_authopenid.signals import oid_associate

from busylizzy.blproject.models import Project

import random

RESPONSE_CHOICES = (
    (1, _('None')),
    (2, _('Accepted')),
    (3, _('Declined')),
)

class InviteManager(models.Manager):
    """ Manager for inviting users into you project """
    def get_suggestions(self, user, project):
        """ Returns possible new members for a user in a project """
        projects = Project.objects.filter(members=user).exclude(pk=project.id).distinct()
        invites_send = [i.created_for_user for i in self.filter(project=project, response=1)]

        suggestions = []
        for p in projects:
            new = [m for m in p.members.all() 
                   if m not in suggestions              # Shouldn't be already suggested.
                   and m not in project.members.all()   # Shouldn't be in the project.
                   and m not in invites_send]           # Shouldn't have a open invite
            suggestions += new
        return suggestions

    def create_invite_user(self, created_by, project, created_for_user):
        """ Creates a new invite for a user """
        # Check for who the invite is for
        sha = self.create_sha(project, created_for_user.username)
        invite = self.create(sha=sha,
                             created_by=created_by,
                             project=project,
                             created_for_user=created_for_user,
                             created_for_email=created_for_user.email)

        # Send user an e-mail that he's invited
        subject = _('You received an invitation to join %(project)s' % {'project': project.name})
        created_by_name = created_by.first_name if created_by.first_name else created_by.username
        if created_by.first_name and created_by.last_name: created_by_name += ' %s' % created_by.last_name

        body = render_to_string('blinvite/user_invite.txt', {'username': created_for_user.username,
                                                             'created_by': created_by_name,
                                                             'project': project.name,
                                                             'sha': sha})

        send_mail(subject, body, settings.EMAIL_FROM, [created_for_user.email], fail_silently=False) 
        return invite

    def create_invite_email(self, created_by, project, addresses):
        """
        Sends an invite to all e-mail addresses that are supplied

        @TODO: Should I be using BCC?
        
        """
        subject = _('You received an invitation to join %(project)s' % {'project': project.name})
        created_by_name = created_by.first_name if created_by.first_name else created_by.username

        for a in addresses:
            sha = self.create_sha(project, a)
            body = render_to_string('blinvite/email_invite.txt', {'created_by': created_by_name,
                                                                  'project': project.name,
                                                                  'sha': sha})
            invite = self.create(sha=sha,
                                 created_by=created_by,
                                 project=project,
                                 created_for_user=None,
                                 created_for_email=a)
            send_mail(subject, body, settings.EMAIL_FROM, [a], fail_silently=False)
        return addresses

    def create_sha(self, project, created_for):
        """ Creates a unique SHA which the user can respond to """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        return sha_constructor(project.name + salt + created_for).hexdigest()

    def register_signal(self, user, openid=None, **kwargs):
        """ Things to do when a user registers """
        invites = self.filter(created_for_email__iexact=user.email)
        for i in invites:
            # Connect the user to the invites
            i.created_for_user = user
            # Handle the responses
            if i.response == 2:
                i.project.members.add(user)
            i.save()

class Invite(models.Model):
    """ A base model for invites """
    sha = models.CharField(_('sha'), max_length=40)
    date = models.DateField(_('date'), auto_now_add=True)
    response = models.PositiveIntegerField(choices=RESPONSE_CHOICES, default=1)
    project = models.ForeignKey(Project, related_name='')

    created_by = models.ForeignKey(User, related_name='send_invites')
    created_for_user = models.ForeignKey(User, related_name='created_invites', blank=True, null=True)
    created_for_email = models.EmailField(blank=True, null=True)

    objects = InviteManager()

    def __unicode__(self):
        created_for = self.created_for_user.username if self.created_for_user else self.created_for_email
        return '%(created_by)s invited %(created_for)s for %(project)s' % {'created_by': self.created_by.username,
                                                                           'created_for': created_for,
                                                                           'project': self.project.name}

user_registered.connect(Invite.objects.register_signal)
oid_associate.connect(Invite.objects.register_signal)
