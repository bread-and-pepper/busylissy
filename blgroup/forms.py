import authority
import re

from django import forms
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from authority.models import Permission
from tagging.models import Tag
from tagging.utils import parse_tag_input

from busylizzy.blgroup.models import Group
from busylizzy.blproject.models import Project
from busylizzy.blmessage.widgets import WMDEditor

def _grant_permission(codename, model, model_object, user, approved=True):
    permission = Permission(codename=codename,
                            content_type=ContentType.objects.get_for_model(model),
                            object_id=model_object.id,
                            user=user,
                            approved=approved)
    permission.save()

    return permission

class GroupForm(ModelForm):
    class Meta:
        model = Group
        exclude = ('slug', 'members', )

    def clean_tags(self):
        tag_list = parse_tag_input(self.cleaned_data['tags'])
        tags = ''
        for tag in tag_list:
            tag = tag.lower().replace(' ', '-')
            if tag not in tags:
                tags += tag + ","

        # Project name must always be a tag
        group_tag = slugify(self.cleaned_data['name'])
        if group_tag not in tag_list:
            tags = group_tag + ',' + tags

        return tags

    def save(self, user, group_slug=None, force_insert=False, force_update=False, commit=True):
        group = super(GroupForm, self).save(commit=False)

        group.slug = slugify(self.cleaned_data['name'])
        if commit:
            group.save()

            if not group_slug:
                group.members =  [user.id, ]

                # Give the creator permission to change and delete
                _grant_permission('group_permission.change_group', Group, group, user)
                _grant_permission('group_permission.delete_group', Group, group, user)

        return group

class GroupProjectForm(ModelForm):
    description = forms.CharField(_("description"), widget=WMDEditor)
    members = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    
    class Meta:
        model = Project
        exclude = ('slug', 'members', 'description')
        fields = ['name', 'description', 'url', 'image', 'status', 'tags', 'members',]

    def __init__(self, group, *args, **kwargs):
        super(GroupProjectForm, self).__init__(*args, **kwargs)
        self.fields['members'].queryset = User.objects.filter(group_members__in=[group.id])

    def clean_tags(self):
        tag_list = parse_tag_input(self.cleaned_data['tags'])
        tags = ''
        for tag in tag_list:
            tag = tag.lower().replace(' ', '-')
            if tag not in tags:
                tags += tag + ","

        return tags

    def save(self, user, force_insert=False, force_update=False, commit=True):
        project = super(GroupProjectForm, self).save(commit=False)

        slug = slugify(self.cleaned_data['name'])
        allSlugs = [sl.values()[0] for sl in Project.objects.exclude(pk=project.id).values("slug")]
        if slug in allSlugs:
            counterFinder = re.compile(r'-\d+$')
            counter = 2
            slug = "%s-%i" % (slug, counter)
            while slug in allSlugs:
                slug = re.sub(counterFinder,"-%i" % counter, slug)
                counter += 1

        project.slug = slug
        if commit:
            project.description = self.cleaned_data['description']
            project.save()

            # Save members
            for member in self.cleaned_data['members']:
                project.members.add(member.id)

            # Give the creator permission to change and delete
            _grant_permission('project_permission.change_project', Project, project, user)
            _grant_permission('project_permission.delete_project', Project, project, user)

            # Tag the project with its name
            Tag.objects.add_tag(project, project.slug)

        return project
        
        
