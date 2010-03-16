from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.forms.fields import email_re

from busylissy.blinvite.models import Invite

class MultiUserField(forms.Field):
    def clean(self, value):
        """ 
        Check that the field contains on or more comma-seperated users and
        normalizes the data to a list of usernames 
        
        """
        if not value:
            raise forms.ValidationError(_('Enter at least one username'))
        usernames = [u.strip() for u in value.split(',') if u.strip() != '']
        users = []
        for u in usernames:
            try:
                users.append(User.objects.get(username__iexact=u))
            except User.DoesNotExist:
                raise forms.ValidationError(_('%(username)s is not registered at BusyLissy') % {'username': u})
        return users

class InviteUserForm(forms.Form):
    """ Invite a user to your project """
    usernames = MultiUserField(label=_('usernames'))

    def __init__(self, project, *args, **kwargs):
        super(InviteUserForm, self).__init__(*args, **kwargs)
        self.project = project

    def clean_usernames(self):
        for user in self.cleaned_data['usernames']:
            # Check if username is already part of the project
            if user in self.project.members.all():
                raise forms.ValidationError(_('%(username)s is already a member of %(project)s.' % {'username': user.username,
                                                                                                    'project': self.project.name}))
            # Check if username already got an open invite
            if len(Invite.objects.filter(project=self.project, created_for_user=user, response=1)) > 0:
                raise forms.ValidationError(_('%(username)s already got an invite for this project.' % {'username': user.username}))
        return self.cleaned_data['usernames']

    def save(self, user):
        """ Save and send the invite """
        amount = 0
        for created_for in self.cleaned_data['usernames']:
            invite = Invite.objects.create_invite_user(user, self.project, created_for)
            amount += 1
        return amount

class MultiEmailField(forms.Field):
    def clean(self, value):
        """
        Check that the field contains one or more comma-separated emails
        and normalizes the data to a list of the email strings.
        """
        if not value:
            raise forms.ValidationError('Enter at least one e-mail address.')
        emails = [e.strip() for e in value.split(',') if e.strip() != ""]
        for email in emails:
            if not email_re.match(email):
                raise forms.ValidationError(_('%(email)s is not a valid e-mail address.' % {'email': email}))

        # Always return the cleaned data.
        return emails

class InviteEmailForm(forms.Form):
    """ Invite a unregistered user to your project """
    email_addresses = MultiEmailField(label=_('email_addresses'))
    pm = forms.CharField(label=_('personal message'), widget=forms.Textarea())
    
    def __init__(self, project, *args, **kwargs):
        super(InviteEmailForm, self).__init__(*args, **kwargs)
        self.project = project

    def clean_email_addresses(self):
        for e in self.cleaned_data['email_addresses']:
            # Check if an invite is already sent out.
            invites = Invite.objects.filter(created_for_email__iexact=e, project=self.project, response=1).count()
            if invites > 0:
                raise forms.ValidationError(_('%(email)s already got an invite for this project.' % {'email': e}))
            # Check if user is already a member of the project.
            if e in [m.email for m in self.project.members.all()]:
                raise forms.ValidationError(_('%(email)s is already a member of this project' % {'email': e}))
        return self.cleaned_data['email_addresses']

    def save(self, user):
        """ Save and send the invite, returns the amount of users and a list of e-mails send out """
        # Check if some of the addresses are registered users
        users_send = 0
        for e in self.cleaned_data['email_addresses']:
            try:
                created_for = User.objects.get(email__iexact=e)
            except User.DoesNotExist: pass
            else:
                Invite.objects.create_invite_user(user, self.project, created_for)
                users_send += 1
                self.cleaned_data['email_addresses'].remove(e)
        emails_send = Invite.objects.create_invite_email(user, self.project, self.cleaned_data['email_addresses'])
        return (users_send, emails_send)
