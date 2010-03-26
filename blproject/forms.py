import authority
import re

from django.conf import settings
from django import forms
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from busylissy.blproject.models import Project
from authority.models import Permission
from tagging.models import Tag
from tagging.utils import parse_tag_input

from busylissy.blmessage.widgets import WMDEditor

def _grant_permission(codename, model, model_object, user, approved=True):
    permission = Permission(codename=codename,
                            content_type=ContentType.objects.get_for_model(model),
                            object_id=model_object.id,
                            user=user,
                            approved=approved)
    permission.save()

    return permission

class ProjectForm(forms.ModelForm):
    description = forms.CharField(_("description"), widget=WMDEditor)

    class Meta:
        model = Project
        exclude = ('slug', 'members', 'image', 'url', )

    def clean_name(self):
        if self.cleaned_data['name'] in settings.DISALLOWED_PROJECTS:
            raise forms.ValidationError(_('Project name is not allowed'))
        else:
            return self.cleaned_data['name']
        
    def clean_tags(self):
        tag_list = parse_tag_input(self.cleaned_data['tags'])
        tags = ''
        for tag in tag_list:
            tag = slugify(tag)
            if tag not in tags:
                tags += tag + ","

        # Project name must always be a tag
        # getting name field if not cleaned
        name = self.fields["name"] or self.cleaned_data["name"]
        project_tag = slugify(name) # getting name field
        if project_tag not in tag_list:
            tags = project_tag + ',' + tags
                
        return tags

    def save(self, user, project_slug=None, force_insert=False, force_update=False, commit=True):
        project = super(ProjectForm, self).save(commit=False)

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
            project.save()

            if not project_slug:
                project.members = [user.id, ]

                # Give the creator permission to change and delete
                _grant_permission('project_permission.change_project', Project, project, user)
                _grant_permission('project_permission.delete_project', Project, project, user)

        return project
