from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout

from django_authopenid.forms import *
from registration.forms import RegistrationFormUniqueEmail

from busylissy.blinvite.models import Invite
from busylissy.blinvite.forms import InviteUserForm, InviteEmailForm
from busylissy.blproject.permissions import ProjectPermission
from busylissy.blproject.models import Project

INITIAL_INVITE_PM = _('I would like to add you to my project on BusyLissy.')

def index(request, project_slug):
    """ Invite for a project """
    # Get Project
    project = get_object_or_404(Project, slug=project_slug, members=request.user)
    
    # Get Permissions
    perm = ProjectPermission(request.user)
    if not perm.change_project(project):
        raise Http404

    # Member suggestions
    suggestions = Invite.objects.get_suggestions(request.user, project)

    # Forms
    user_form = InviteUserForm(project)

    initial_email = {'pm': INITIAL_INVITE_PM,}
    email_form = InviteEmailForm(project, initial=initial_email)

    if request.method == "POST":
        # Which form was posted?
        if request.POST.has_key('usernames'):
            user_form = InviteUserForm(project, request.POST)
            if user_form.is_valid():
                invites = user_form.save(request.user)
                request.user.message_set.create(message=_('%(amount)s invite(s) has been sent out.' % {'amount': invites}))
                return HttpResponseRedirect(reverse('project-detail', kwargs={'slug': project.slug}))

        elif request.POST.has_key('email_addresses'):
            email_form = InviteEmailForm(project, request.POST)
            if email_form.is_valid():
                (useri, emaili) = email_form.save(request.user)
                if len(emaili) == 1 and useri == 0:
                    request.user.message_set.create(message=_('Your invite to %(invited)s has been sent out.' % {'invited': emaili[0]}))
                else:
                    request.user.message_set.create(message=_('%(amount)s invites has been sent out.' % {'amount': useri + len(emaili)}))
                return HttpResponseRedirect(reverse('project-detail', kwargs={'slug': project.slug}))

    extra_context = {'user_form': user_form,
                     'email_form': email_form,
                     'project': project,
                     'members': suggestions}

    return direct_to_template(request,
                              template='blinvite/index.html',
                              extra_context=extra_context)

def response(request, invite_key, answer='y'):
    """ When an invite is accepted or declined """
    invite = get_object_or_404(Invite, sha=invite_key, response=1)
    invite.response = 2 if answer == "y" else 3
    invite.sha = "ALREADY_USED"
    invite.save()
    # Accepted
    if answer == 'y':
        # User is authenticated, and the user that is asked, than redirect to project
        if request.user.is_authenticated() and request.user == invite.created_for_user:
            invite.project.members.add(request.user)
            request.user.message_set.create(message=_('You have been added to %(project)s.' % {'project': invite.project.name}))
            return HttpResponseRedirect(reverse('project-list'))
        # User is authenticated as a different user
        elif request.user.is_authenticated() and invite.created_for_user:
            invite.project.members.add(invite.created_for_user)
            request.user.message_set.create(message=_('%(username)s has been added to %(project)s. \
                                                      Login as him to go to this project.' % {'username': invite.created_for_user.username,
                                                                                              'project': invite.project.name}))
            logout(request)
            return HttpResponseRedirect(reverse('user_signin'))
        # User is registered but not authenticated
        elif invite.created_for_user:
            invite.project.members.add(invite.created_for_user)
            return HttpResponseRedirect(reverse('user_signin') + '?next=%(project_url)s' % {'project_url': reverse('project-detail', kwargs={'slug': invite.project.slug})})
        # User is not registered and not authenticated
        else:
            form = RegistrationFormUniqueEmail(initial={'email': invite.created_for_email})
            return direct_to_template(request,
                                      template='blinvite/pos_response.html',
                                      extra_context={'form': form,
                                                     'project': invite.project})
    
    # User doesn't want to join the project.
    if answer == 'n':
        # User is registered.
        if invite.created_for_user:
            if request.user.is_authenticated():
                request.user.message_set.create(message=_('You have declined the invitation to %(project)s.' % {'project': invite.project.name}))
                return HttpResponseRedirect(reverse('project-list'))
            else:
                return direct_to_template(request,
                                          template='blinvite/neg_reg_response.html')
        # User is not registered.
        else:
            return direct_to_template(request,
                                      template='blinvite/neg_anon_response.html')
