import datetime
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import list_detail, create_update
from django.utils.translation import ugettext as _

from busylizzy.bltask.forms import TaskModelForm
from busylizzy.bltask.models import Task
from busylizzy.bltask.utils import structure
from busylizzy.blproject.models import Project
from busylizzy.blactivity.models import Activity

from tagging.models import Tag, TaggedItem

@login_required
def move(request, project_slug, id, sibling):
    """ Moves a task to another parent """
    pass

@login_required
def task_project_list(request, project_slug):
    """ 
    Lists all tasks for a project. Also looks for a optional depth ``GET``
    argument which supplies the depth of the tree.
    
    """
    project = get_object_or_404(Project, slug=project_slug, members=request.user)
    depth = request.GET.get('depth', None)
    all_nodes = Task.my_objects.get_nodes_for_project(project, depth) 
    tags = Tag.objects.usage_for_queryset(Task.objects.select_related().filter(project=project),
                                          counts=True)

    return direct_to_template(request,
                              template='bltask/list.html',
                              extra_context={
                                  'nodes': structure(all_nodes),
                                  'nodes_count': len(all_nodes),
                                  'project': project,
                                  'task_tags': tags})

@login_required
def add_edit(request, project_slug, instance=None, parent=None):
    """ Add or edit a task to a project """
    project = get_object_or_404(Project, slug=project_slug, members=request.user)
    tags = Tag.objects.usage_for_queryset(Task.objects.select_related().filter(project=project),
                                          counts=True)
    if instance: instance = get_object_or_404(Task, id=instance)
    if parent: parent = get_object_or_404(Task, id=parent)
    initial = {'assigned_to': request.user.id }
    
    form = TaskModelForm(project,
                         request.user,
                         parent,
                         instance=instance,
                         initial=initial if not instance else None)

    if request.method == "POST":
        form = TaskModelForm(project,
                             request.user,
                             parent,
                             request.POST,
                             instance=instance)
        if form.is_valid():
            task = form.save()
            
            # Message notification
            if instance:
                msg = _('Task \'%(name)s\' has been updated' % {'name': task.name})
                task.create_activity(request.user, Activity.UPDATE) 
            else:
                msg = _('Task \'%(name)s\' has been created' % {'name': task.name})
                task.create_activity(request.user, Activity.CREATE)
                # If the task has siblings, move to the top
                sibling = task.get_siblings()[0]
                if sibling:
                    task.move(sibling, 'first-sibling')

            request.user.message_set.create(message=msg)

            return HttpResponseRedirect(reverse('task-list', 
                                                kwargs={'project_slug': project_slug}) + \
                                        "#task-%s" % task.id)

    return direct_to_template(request,
                              template='bltask/task_form.html',
                              extra_context={
                                  'form': form,
                                  'project': project,
                                  'tags': tags,})

@login_required
def delete(request, project_slug, id):
    """ Delete a node 
    
    TODO:
        - Confirmation of delete
        - Notification of delete
    
    """
    node = get_object_or_404(Task, id=id, project__members=request.user)
    node.create_activity(request.user, Activity.DELETE)
    node.delete()
    request.user.message_set.create(message=_('Task \'%(name)s\' has been deleted' % {'name': node.name}))
    return HttpResponseRedirect(reverse('task-list', kwargs={'project_slug': project_slug}))

@login_required
def tagged_tasks(request, project_slug, tags=None):
    """ Return tagged tasks """
    tag_list = tags.split("+")
    
    task_queryset = Task.objects.filter(project__slug=project_slug)
    queryset = TaggedItem.objects.get_intersection_by_model(task_queryset, tag_list)

    all_nodes = [(node, node.get_children_count()) for node in queryset]
    tags = Tag.objects.usage_for_queryset(queryset, counts=True)
    project = Project.objects.get(slug=project_slug)
    
    selected_tags = []
    tag_url = ''
    for item in tag_list:
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)
        tag_url += item + '+'

    return direct_to_template(request,
                              template='bltask/list.html',
                              extra_context={'nodes': structure(all_nodes),
                                             'nodes_count': len(all_nodes),
                                             'task_tags': tags,
                                             'tag_url': tag_url,
                                             'selected_tags': selected_tags,
                                             'project': project })
@login_required
def toggle(request, project_slug, id):
    """ Toggles a task as complete or incomplete """
    task = get_object_or_404(Task, id=id, project__members=request.user)
    if task.toggle():
        if task.completed:
            msg = _('Task \'%(name)s\' has been completed' % {'name': task.name})
            task.create_activity(request.user, Activity.CLOSE)
            # Move the node to the correct position
            try:
                last_completed = task.get_siblings().filter(completed=True).exclude(pk=task.pk)[0]
            except IndexError:
                task.move(task, 'last-sibling')
            else:
                task.move(last_completed, 'left')
        else:
            msg = _('Task \'%(name)s\' has been marked as incomplete' % {'name': task.name})
            # Move it to the correct position
            task.move(task, 'first-sibling')

        request.user.message_set.create(message=msg)
    return HttpResponseRedirect(reverse('task-list', kwargs={'project_slug': project_slug}) + \
                               '#task-%s' % task.id)

def week_cal(request, project_slug, direction, today=None):
    """ Return calendar """
    now = datetime.datetime.now()

    if today is None:
        today = now
    else: today = datetime.datetime.strptime(today + '-' + str(now.year), "%d-%m-%Y")
    if direction == "forw":
        today = today + datetime.timedelta(days=1)
    else: today -= datetime.timedelta(days=8)
    
    if today.month < now.month or (today.year - now.year) != 0:
        today = today.replace(year=today.year + 1)

    end_of_week = today + datetime.timedelta(days=7)

    milestone_list = Task.objects.filter(project__slug=project_slug, completed=False, due_date__lte=end_of_week).order_by("-due_date")
    project = get_object_or_404(Project, slug=project_slug)

    days = []

    day = today
    while day <= end_of_week:
        cal_day = {}
        cal_day['day'] = day
        cal_day['milestone'] = False

        for item in milestone_list:
            if item.due_date and (day.date() == item.due_date):
                cal_day['milestone'] = True
                cal_day['event'] = item
                
        days.append(cal_day)
        day += datetime.timedelta(days=1)

    return direct_to_template(request,
                              template='bltask/cal.html',
                              extra_context={'days':days, 'project': project})
