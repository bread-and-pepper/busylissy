from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from busylizzy.bltask.models import Task

from tagging.forms import TagField
from tagging.utils import parse_tag_input

import datetime

class TaskModelForm(forms.ModelForm):
    def clean_tags(self):
        tag_list = parse_tag_input(self.cleaned_data['tags'])
        tags = ''
        for tag in tag_list:
            tag = tag.replace(' ', '-')
            if tag not in tags:
                tags += tag + ","

        return tags
    
    class Meta:
        model = Task
        fields = ('name', 'note', 'due_date', 'tags', 'assigned_to')

    def __init__(self, project, user, parent=None, *args, **kwargs):
        self.project = project
        self.parent = parent
        self.user = user

        super(TaskModelForm, self).__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(project_members__in=[self.project.id,])

    def save(self, commit=True):
        if self.instance.id:
            # Just an update, do the normal stuff
            return super(TaskModelForm, self).save()
        else:
            if self.parent:
                add_method = self.parent.add_child
            else:
                add_method = Task.add_root

            return add_method(name=self.cleaned_data['name'],
                              note=self.cleaned_data['note'],
                              due_date=self.cleaned_data['due_date'],
                              tags=self.cleaned_data['tags'],
                              assigned_to=self.cleaned_data['assigned_to'],
                              project=self.project,
                              created_by=self.user,
                              created_at=datetime.datetime.now())
