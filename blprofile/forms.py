from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.db.models import get_model
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.template import loader, Context
from django.contrib.contenttypes.models import ContentType

import re

from busylizzy.blprofile.models import UserProfile
from django.contrib.auth.models import User

attrs_dict = {'class': 'required' }
alnum_re = re.compile(r'^[- \w]+$')
alnum_multi_re = re.compile(r'^[- ,\w]+$')

class ProfileForm(ModelForm):
    first_name = forms.RegexField(regex=alnum_re,
                                  error_messages={'invalid':_(u'Can only contain letters, numbers and spaces')},
                                  max_length=30,
                                  min_length=3,
                                  widget=forms.TextInput(attrs=attrs_dict),
                                  label=_(u'First name'))

    last_name = forms.RegexField(regex=alnum_re,
                                 error_messages={'invalid':_(u'Can only contain letters, numbers and spaces')},
                                 max_length=30,
                                 min_length=3,
                                 widget=forms.TextInput(attrs=attrs_dict),
                                 label=_(u'Last name'))

    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               max_length=75)),
                             label=_(u'Email'))
    
    class Meta:
        model = UserProfile
        exclude = ('user', )
        fields = ['first_name', 'last_name', 'email', 'website', 'about_me',  'avatar', ]

    def save(self, user, force_insert=False, force_update=False, commit=True):
        profile = super(ProfileForm, self).save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()

        profile.user = user
        if commit:
            profile.save()
        
        return profile

class SettingsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['notifications', 'is_public', 'language']
        
        
class MemberForm(forms.Form):
    username = forms.RegexField(regex=alnum_multi_re,
                                error_messages={'invalid':_(u'Username contains only letters and numbers')},
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'username'))

    def clean_username(self):
        """
        Validation of the username
        - user must be existent
        """
        if self.cleaned_data['username'].strip()[-1:] == ",":
            self.cleaned_data['username'] = self.cleaned_data['username'].strip()[:-1]

        usernames = self.cleaned_data['username'].split(",")

        error = False
        for username in usernames:
            try:
                user = User.objects.get(username__iexact=username.strip())
            except User.DoesNotExist:
                error = True

        if error:
            if len(usernames) > 1:
                error_message = _("One of the usernames does not exist")
            else: error_message = _("Username does not exist")
            raise forms.ValidationError(error_message)
        else:
            return self.cleaned_data['username']

    def save(self, model, model_id):
        instance = model.objects.get(pk=model_id)
        ctype = ContentType.objects.get_for_model(instance)
        
        usernames = self.cleaned_data['username'].split(",")
        
        for username in usernames:
            member = User.objects.get(username__iexact=username.strip())
            #try:
                # Check if invite exist
            #except Invite.DoesNotExist:
             #   if member not in instance.members.all():
                    # Send notification
        return usernames

class InviteForm(forms.Form):
    email = forms.EmailField(label=_(u'email address'))

    def save(self, user,  model, model_id, force_insert=False, force_update=False, commit=True):
        template = loader.get_template('blprofile/invite.txt')
        instance = model.objects.get(pk=model_id)
        
        context = Context({'email': self.cleaned_data['email'],
                           'instance': instance,
                           'user': user})
        
        subject = _('BusyLissy: Invite for') + " " +instance.name
        message = template.render(context)
        invite_email = self.cleaned_data['email']

        send_mail(subject, message, user.email, [invite_email,])

        return invite_email
