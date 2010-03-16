from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from busylissy.blmessage.models import Thread, Message
from busylissy.blmessage.widgets import WMDEditor
from busylissy.blproject.models import Project

from tagging.utils import parse_tag_input

class ThreadForm(forms.ModelForm):
    message = forms.CharField(_('message'), widget=WMDEditor)

    def clean_message(self):
        if len(self.cleaned_data['message']) <= 5:
            raise forms.ValidationError(_('Message should be longer than 5 characters.'))
        return self.cleaned_data['message']

    def clean_tags(self):
        tag_list = parse_tag_input(self.cleaned_data['tags'])
        tags = ''
        for tag in tag_list:
            tag = tag.replace(' ', '-')
            if tag not in tags:
                tags += tag + ","
    
        return tags

    class Meta:
        model = Thread
        exclude = ('latest_message_time', 'closed', 'message_count', 'content_type', 'object_id', 'seen_by')

    def save(self, object, user, force_insert=False, force_update=False, commit=True):
        thread = super(ThreadForm, self).save(commit=False)
        thread.content_type = ContentType.objects.get_for_model(object)
        thread.object_id = object.id

        if commit:
            thread.save()
            thread.seen_by = [user.pk, ]
            m = Message(thread=thread, author=user, body=self.cleaned_data['message'])
            m.save()
            
        return thread

class EditThreadForm(forms.ModelForm):
    def clean_tags(self):
        tag_list = parse_tag_input(self.cleaned_data['tags'])
        tags = ''
        for tag in tag_list:
            tag = tag.lower().replace(' ', '-')
            if tag not in tags:
                tags += tag + ","

        return tags
    
    class Meta:
        model = Thread
        exclude = ('latest_message_time', 'closed', 'message_count', 'content_type', 'object_id', 'seen_by')

    def save(self, object, user, force_insert=False, force_update=False, commit=True):
        thread = super(EditThreadForm, self).save(commit=False)
        thread.content_type = ContentType.objects.get_for_model(object)
        thread.object_id = object.id

        if commit:
            thread.save()
            thread.seen_by = [user.pk, ]
            
        return thread
        
    
class MessageForm(forms.ModelForm):
    body = forms.CharField(_("body"), widget=WMDEditor)

    class Meta:
        model = Message
        exclude = ('thread', 'author', 'body', )

    def clean_body(self):
        if len(self.cleaned_data['body']) <= 5:
            raise forms.ValidationError(_('Message should be longer than 5 characters.'))
        return self.cleaned_data['body']

    def save(self, thread, user, force_insert=False, force_update=False, commit=True):
        message = super(MessageForm, self).save(commit=False)
        thread.seen_by = [user.pk, ]
        thread.save()
        
        message.body = self.cleaned_data['body']
        message.thread = thread
        message.author = user
        
        if commit:
            message.save()

        return message

class FeedbackForm(forms.Form):
    body = forms.CharField(_("body"), widget=forms.Textarea)

    def save(self, user, force_insert=False, force_update=False, commit=True):
        project = Project.objects.get(slug='busy-lissy')
        
        try:
            thread = Thread.objects.get(content_type=ContentType.objects.get_for_model(project),
                                        object_id=project.id,
                                        title='Feedback')
        except Thread.DoesNotExist:
            thread = Thread(title='Feedback',
                            content_type=ContentType.objects.get_for_model(project),
                            object_id=project.id,
                            )
            thread.save()

        message = Message(body=self.cleaned_data['body'],
                          thread=thread,
                          author=user)
        
        if commit:
            message.save()

        return message
