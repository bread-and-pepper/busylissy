from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from tagging.views import tagged_object_list

from tagging.models import Tag, TaggedItem
from django.contrib.auth.models import User

from busylizzy.blgroup.models import Group
from busylizzy.blgroup.forms import GroupForm, GroupProjectForm
from busylizzy.blgroup.permissions import GroupPermission

@login_required
def list(request):
    queryset = Group.objects.filter(members=request.user)
    tags = Tag.objects.usage_for_queryset(queryset, counts=True)
    
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   template_name='blgroup/group_list.html',
                                   template_object_name='group',
                                   extra_context={'group_tags': tags})

@login_required
def detail(request, slug):
    """ Views a certain group """
    return list_detail.object_detail(request,
                                     queryset=Group.objects.filter(members=request.user),
                                     slug=slug,
                                     template_name='blgroup/detail.html',
                                     template_object_name='group',)

@login_required
def add_edit(request, slug=None):
    """ Add/Edit group """
    form = GroupForm(request.POST or None,
                     instance=slug and Group.objects.get(slug__iexact=slug))

    if slug:
        check = GroupPermission(request.user)
        group = Group.objects.get(slug__iexact=slug)
        if not check.change_group(group):
            raise Http404
        
    if request.method == "POST" and form.is_valid():
        group = form.save(request.user, slug)
        form.save_m2m()

        # Notification
        if slug: msg = _("Group '%(group)s' has been updated" % {'group': group.name })
        else: msg = _("Group '%(group)s' has been created" % {'group': group.name })
        request.user.message_set.create(message=msg)

        return HttpResponseRedirect(reverse('group-detail', kwargs = {'slug': group.slug }))

    return direct_to_template(request,
                              template='blgroup/form.html',
                              extra_context={'form': form, })

@login_required
def delete(request, slug):
    """ Delete group """
    group = get_object_or_404(Group, slug__iexact=slug)
    check = GroupPermission(request.user)
    
    if check.delete_group(group):
        group.delete()

        # Notification
        request.user.message_set.create(message=_("Group '%(group)s' has been deleted" % {'group': group.name }))
        
        return HttpResponseRedirect(reverse('group-list'))
    else:
        raise Http404

@login_required
def start_project(request, slug):
    """ Start project as group """
    group = get_object_or_404(Group, slug__iexact=slug)
    data = {'members': [request.user.id] }
    form = GroupProjectForm(group, request.POST or None, initial=data)

    if request.method == "POST" and form.is_valid():
        project = form.save(request.user)

        return HttpResponseRedirect(reverse('project-detail',
                                            kwargs = {'slug': project.slug}))

    return direct_to_template(request,
                              template='blgroup/form_project.html',
                              extra_context={'form': form,
                                             'group': group})

@login_required
def tagged_groups(request, tags=None):
    """ List tagged objects """
    tag_list = tags.split("+")
    
    queryset = TaggedItem.objects.get_intersection_by_model(Group.objects.filter(members=request.user), tag_list)
    tags = Tag.objects.usage_for_queryset(queryset, counts=True)

    selected_tags = []
    for item in tag_list:
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)
        tag_url = item + '+'

    return list_detail.object_list(request,
                                   queryset=queryset,
                                   template_name='blgroup/group_list.html',
                                   template_object_name='group',
                                   extra_context={'group_tags': tags,
                                                  'tag_url': tag_url,
                                                  'selected_tags': selected_tags})

