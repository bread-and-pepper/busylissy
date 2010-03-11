from itertools import chain
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from authority.decorators import permission_required_or_403
from django.http import HttpResponseRedirect, Http404
from django.views.generic import list_detail
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import ugettext as _

from tagging.views import tagged_object_list
from tagging.models import Tag, TaggedItem
from tagging.utils import LOGARITHMIC, calculate_cloud

from busylizzy.blproject.models import Project
from busylizzy.blproject.forms import ProjectForm
from busylizzy.blproject.permissions import ProjectPermission
from busylizzy.blmessage.models import Thread
from busylizzy.bltask.models import Task
from busylizzy.blactivity.models import Activity
from busylizzy.blinvite.models import Invite

def index(request):
    """ Index page """
    if request.user.is_authenticated():
        return list(request)
    else:
        return direct_to_template(request,
                                  template='static/index.html',)

@login_required
def list(request):
    """ List all projects """
    tags = Tag.objects.usage_for_queryset(Project.objects.filter(members=request.user, status=2), counts=True)
    notices = Invite.objects.filter(response=1, created_for_user=request.user)[:1]
    project_list = Project.objects.ordered_projects(request.user)

    return list_detail.object_list(request,
                                   queryset=Project.objects.all(),
                                   template_name='blproject/project_list.html',
                                   extra_context={'project_tags': tags,
                                                  'project_list': project_list,
                                                  'notices': notices})

@login_required
def list_by_status(request, status):
    """ List all projects by status """
    choices = {'finished': '3', 'active': '2', 'hold': '1'}
    tags = Tag.objects.usage_for_queryset(Project.objects.filter(members=request.user, status=choices[status]), counts=True)
    project_list = Project.objects.ordered_projects(request.user, choices[status])
    
    return list_detail.object_list(request,
                                   queryset=Project.objects.all(),
                                   template_name='blproject/project_list.html',
                                   extra_context={'project_tags': tags,
                                                  'active': 'projects-'+status,
                                                  'project_list': project_list})

@login_required
def detail(request, slug, type=None):
    """ Detail page of a project """
    project = get_object_or_404(Project, slug=slug)
    project_type = ContentType.objects.get_for_model(project)
    
    task_tags = Tag.objects.usage_for_queryset(Task.objects.select_related().filter(project__slug=slug), counts=True)
    thread_tags = Tag.objects.usage_for_queryset(Thread.objects.filter(content_type__pk=project_type.pk,
                                                                       object_id=project.id), counts=True)

    all_tags = task_tags + thread_tags
    all_tags = reduce(lambda l, x: x not in l and l.append(x) or l, all_tags, [])

    tags = calculate_cloud(all_tags, 4, LOGARITHMIC)

    return list_detail.object_detail(request,
                                     queryset=Project.objects.filter(members=request.user),
                                     slug=slug,
                                     template_name='blproject/detail.html',
                                     template_object_name='project',
                                     extra_context={'tag_cloud': tags },
                                     )

@login_required 
def add_edit(request, slug=None):
    """ Add/Edit Project """
    form = ProjectForm(request.POST or None,
                       instance=slug and Project.objects.get(slug__iexact=slug))

    tags = Tag.objects.usage_for_queryset(Project.objects.filter(members=request.user), counts=True)
    project = None
    if slug:
        check = ProjectPermission(request.user)
        project = Project.objects.get(slug__iexact=slug)
        if not check.change_project(project):
            raise Http404

    if request.method == "POST" and form.is_valid():
        project = form.save(request.user, slug)
        form.save_m2m()

        # Notification
        if slug:
            msg = _("Project '%(project)s' has been updated" % {'project': project.name })
            project.create_activity(request.user, Activity.UPDATE)
        else:
            msg = _("Project '%(project)s' has been created" % {'project': project.name })
            project.create_activity(request.user, Activity.START)
        request.user.message_set.create(message=msg)
        
        return HttpResponseRedirect(reverse('project-detail', kwargs = {'slug': project.slug}))

    return direct_to_template(request,
                              template='blproject/form.html',
                              extra_context={'form':form,
                                             'project': project,
                                             'tags': tags})

@login_required
def delete(request, slug):
    """ Delete project """
    project = get_object_or_404(Project, slug__iexact=slug)
    check = ProjectPermission(request.user)

    if check.delete_project(project):
        project.delete()
        request.user.message_set.create(message=_("Project '%(project)s' has been deleted" % {'project': project.name }))
        
        return HttpResponseRedirect(reverse('project-list'))
    else:
        raise Http404

@login_required
def tagged_projects(request, tags=None):
    """ View projects by tags """
    tag_list = tags.split("+")

    queryset = TaggedItem.objects.get_intersection_by_model(Project.objects.filter(members=request.user), tag_list)
    # retrieve priority
    all_projects = [(project, project.project_value(request.user)) for project in queryset]
    # sort on priority
    all_projects = sorted(all_projects, key=lambda x:(x[1], x[0].latest_activity, x[0].name), reverse=True)

    # Status
    if queryset:
        qs_status = queryset[0].status
        choices = {'1': 'hold', '2': 'active', '3': 'finished'}
        status = choices[str(qs_status)]

    if status in ['hold', 'finished']:
        status = 'projects-'+ status
    else: status = ''

    tags = Tag.objects.usage_for_queryset(queryset, counts=True)

    selected_tags = []
    tag_url = ''
    for item in tag_list:
        tag_url += item + '+'
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)

    return list_detail.object_list(request,
                                   queryset=Project.objects.all(),
                                   template_name='blproject/project_list.html',
                                   extra_context={'project_tags':tags,
                                                  'tag_url': tag_url,
                                                  'selected_tags': selected_tags,
                                                  'active': status,
                                                  'project_list': all_projects})

@login_required
def tagged_items(request, slug, tags=None):
    """ View items tagged in project """
    project = get_object_or_404(Project, slug=slug)
    project_type = ContentType.objects.get_for_model(project)
    
    tag_list = tags.split("+")

    querysets = [Task.objects.select_related().filter(project=project), Thread.objects.filter(content_type__pk=project_type.pk, object_id=project.id)]
    all_tags = []
    qs_items = []
    for query in querysets:
        qs = TaggedItem.objects.get_intersection_by_model(query, tag_list)
        if qs:
            qs_tags = Tag.objects.usage_for_queryset(qs, counts=True)
            all_tags.extend(qs_tags)
            qs_items.extend(qs)

    # Order items and put in cloud
    all_tags = reduce(lambda l, x: x not in l and l.append(x) or l, all_tags, [])
    tags = calculate_cloud(all_tags, 4, LOGARITHMIC)

    # Tagged items
    tagged_items = []
    for item in qs_items:
        item.type = item._meta.module_name
        if hasattr(item, "created_at"):
            item.sort = item.created_at
        else: item.sort = item.latest_message_time
        tagged_items.append(item)
    tagged_items.sort(key=lambda x: x.sort)

    # Complile tags
    selected_tags = []
    tag_url = ''
    for item in tag_list:
        tag_url += item + '+'
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)

    return direct_to_template(request,
                              template='blproject/tagged_item_list.html',
                              extra_context={'tag_cloud': tags,
                                             'tag_url': tag_url,
                                             'selected_tags': selected_tags,
                                             'tagged_items': tagged_items,
                                             'project': project})
    
