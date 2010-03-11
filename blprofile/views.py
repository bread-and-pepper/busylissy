from django.db.models import get_model
from django.views.generic import list_detail, simple
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from authority.models import Permission
from django.utils.translation import ugettext as _

from busylizzy.blprofile.models import UserProfile
from busylizzy.blprofile.forms import MemberForm, ProfileForm, InviteForm, SettingsForm
from busylizzy.blgroup.models import Group
from busylizzy.blproject.models import Project
from busylizzy.blproject.permissions import ProjectPermission
from busylizzy.blgroup.permissions import GroupPermission
from busylizzy.blactivity.models import Activity

@login_required
def view(request):
    """ Redirects to your own profile """
    return HttpResponseRedirect(reverse('profile-detail',
                                        kwargs={'username': request.user.username}))

def list(request):
    """ Returns a list of the users """
    return list_detail.object_list(
        request,
        queryset=UserProfile.objects.public().order_by('-user__date_joined'),
        template_name='blprofile/list.html',
        template_object_name='profile',)

def detail(request, username):
    """ Returns the profile of a single user """
    user = get_object_or_404(User, username=username)

    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        profile = None
    
    return simple.direct_to_template(request,
                                     'blprofile/detail.html',
                                     extra_context={'profile': profile},)

@login_required
def edit(request):
    """ Edit the data of the user """
    user = request.user

    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        profile = None

    data = {'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email}

    form = ProfileForm(instance=profile, initial=data)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile, initial=data)
        if form.is_valid():
            form.save(user)

            # Notification
            request.user.message_set.create(message=_("Your profile has been updated"))
            
            return HttpResponseRedirect(reverse('profile-detail', kwargs = {'username': user.username}))

    return simple.direct_to_template(request,
                                     template='blprofile/edit.html',
                                     extra_context={'form': form,
                                                    'profile' : profile })

@login_required
def delete(request):
    """ Delete the user """
    user = request.user

    try:
        profile = user.get_profile()
        profile.delete()
    except ObjectDoesNotExist:
        profile = None

    user.delete()
    return HttpResponseRedirect(reverse('busylizzy-home'))

@login_required
def add_member(request, model, model_slug, template='blprofile/includes/form.html'):
    """ Add member to model """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=model_slug, members=request.user)

    if isinstance(model_object, Group):
        redirect_reverse = 'group-detail'
        extra_context = {'group': model_object}
        check = GroupPermission(request.user)
        if not check.change_group(model_object):
            raise Http404

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-detail'
        extra_context = {'project': model_object}
        check = ProjectPermission(request.user)
        if not check.change_project(model_object):
            raise Http404

    form = MemberForm()
    invite_form = InviteForm()
    msg = ''

    # Load every member of your projects
    projects = Project.objects.filter(members=request.user).distinct()
    members = []
    for project in projects:
        for member in project.members.all():
            if member not in members and member not in model_object.members.all():
                members.append(member)
        
    if request.method == "POST":
        if 'invite' in request.POST.keys():
            invite_form = InviteForm(request.POST)
            if invite_form.is_valid():
                invite = invite_form.save(request.user, model, model_object.id)
                msg = _("Invite for '%(project)s' has been send to '%(invite)s'" % {'project': model_object.name, 'invite': invite })
        else:
            form = MemberForm(request.POST)
            if form.is_valid():
                members = form.save(model, model_object.id)

                member_string = ''
                for member in members:
                    member_string = member_string + member.strip() + ", "
                if len(members) > 1:
                    msg = _("Members '%(member)s' have been invited to '%(project)s'" % {'member': member_string[:-2], 'project': model_object.name })
                    model_object.create_activity(request.user, Activity.INVITE)
                else:
                    msg = _("Member '%(member)s' has been invited to '%(project)s'" % {'member': member_string[:-2], 'project': model_object.name })
                    user = User.objects.get(username__iexact=member)
                    model_object.create_activity(request.user, Activity.INVITE, user)
                    
        # Notification
        request.user.message_set.create(message=msg)
                
        return HttpResponseRedirect(reverse(redirect_reverse,
                                            kwargs = {'slug': model_slug,}))

    extra_context['form'] = form
    extra_context['inviteform'] = invite_form
    extra_context['members'] = members
    return simple.direct_to_template(request,
                                     template=template,
                                     extra_context=extra_context)

@login_required
def delete_member(request, model, model_slug, member_slug):
    """ Delete member """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=model_slug, members=request.user)

    user = get_object_or_404(User, username=member_slug)

    kwargs = {}
    msg = _("Member '%(member)s' has been removed from '%(project)s'" % {'member': user.username, 'project': model_object.name })
    if isinstance(model_object, Group):
        redirect_reverse = 'group-detail'
        check = GroupPermission(request.user)
        if not check.change_group(model_object):
            raise Http404

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-detail'
        kwargs['slug'] = model_object.slug
        check = ProjectPermission(request.user)
        if not check.change_project(model_object) and user != request.user:
            raise Http404
        if user == request.user:
            redirect_reverse = 'project-list'
            kwargs = {}
            msg = _("You have resigned from '%(project)s'" % {'project': model_object.name })

    if model_object.members.count() > 1:
        model_object.members.remove(user.id)
        model_object.save()

        # Notification
        model_object.create_activity(request.user, Activity.DELETE, user)
        request.user.message_set.create(message=msg)

    return HttpResponseRedirect(reverse(redirect_reverse,
                                        kwargs = kwargs))
    

@login_required
def make_admin(request, model, model_slug, member_slug, permitted=False):
    """ Give administrator rights """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=model_slug, members=request.user)

    user = get_object_or_404(User, username=member_slug)

    if isinstance(model_object, Group):
        redirect_reverse = 'group-detail'
        codename = 'group_permission.change_group'
        check = GroupPermission(request.user)
        if check.change_group(model_object):
            permitted = True

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-detail'
        codename = 'project_permission.change_project'
        check = ProjectPermission(request.user)
        if check.change_project(model_object):
            permitted = True
        
    if permitted:
        permission = Permission(codename=codename,
                                content_type=ContentType.objects.get_for_model(model),
                                object_id=model_object.id,
                                user=user,
                                approved=True)
        permission.save()

        # Notification
        model_object.create_activity(request.user, Activity.ADMIN, user)
        request.user.message_set.create(message=_("Member '%(member)s' has been granted admin permissions for '%(project)s'" % {'member': user.username, 'project': model_object.name }))

    return HttpResponseRedirect(reverse(redirect_reverse,
                                        kwargs = {'slug': model_object.slug}))

@login_required
def settings(request):
    """ Edit settings for the user """
    user = request.user

    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    form = SettingsForm(request.POST or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        form.save()

        # Notification
        request.user.message_set.create(message=_("Your settings have been updated"))
            
        return HttpResponseRedirect(reverse('profile-detail', kwargs = {'username': user.username}))

    return simple.direct_to_template(request,
                                     template='blprofile/settings.html',
                                     extra_context={'profile': profile,
                                                    'form': form })
        

