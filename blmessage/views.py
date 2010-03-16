from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import list_detail
from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _

from tagging.views import tagged_object_list
from tagging.models import Tag, TaggedItem

from busylissy.blmessage.models import Thread, Message
from busylissy.blmessage.forms import ThreadForm, EditThreadForm, MessageForm, FeedbackForm
from busylissy.blgroup.models import Group
from busylissy.blproject.models import Project
from busylissy.blactivity.models import Activity

@login_required
def list_for_model(request, model, object_slug, template='blmessage/list_model.html'):
    model = get_model(*model.split('.'))
    ctype = ContentType.objects.get_for_model(model)
    model_object = get_object_or_404(model,
                                     slug__iexact=object_slug,
                                     members=request.user)

    queryset = Thread.objects.filter(content_type__pk=ctype.id,
                                     object_id=model_object.id)

    tags = Tag.objects.usage_for_queryset(queryset, counts=True)
    if isinstance(model_object, Group):
        redirect_reverse = 'group-thread-detail'
        extra_context = {'group': model_object,}

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-thread-detail'
        extra_context = {'project': model_object,}

    extra_context['thread_tags'] = tags

    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=8,
                                   template_name=template,
                                   template_object_name='thread',
                                   extra_context=extra_context)

@login_required
def detail_for_model(request, model, object_slug, thread_id, template='blmessage/list_message_model.html'):
    model = get_model(*model.split('.'))
    ctype = ContentType.objects.get_for_model(model)
    model_object = get_object_or_404(model,
                                     slug__iexact=object_slug,
                                     members=request.user)

    if isinstance(model_object, Group):
        redirect_reverse = 'group-thread-detail'
        extra_context = {'group': model_object}

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-thread-detail'
        extra_context = {'project': model_object}

    thread = get_object_or_404(Thread, pk=thread_id)
    thread.seen_by.add(request.user)
    thread.save()

    form = MessageForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        message = form.save(thread, request.user)
        thread.create_activity(request.user, Activity.COMMENT)

        # Notification
        request.user.message_set.create(message=_("Your message has been posted"))

        return HttpResponseRedirect(reverse(redirect_reverse,
                                            kwargs = {'object_slug': object_slug,
                                                      'thread_id': thread_id }))

    extra_context['thread'] = thread
    extra_context['form'] = form

    return list_detail.object_list(request,
                                   queryset=thread.messages.all(),
                                   paginate_by=10,
                                   template_name=template,
                                   template_object_name='message',
                                   extra_context=extra_context)

@login_required
def tags_for_model(request, model, object_slug, tags=None):
    model = get_model(*model.split('.'))
    ctype = ContentType.objects.get_for_model(model)
    model_object = get_object_or_404(model,
                                     slug__iexact=object_slug,
                                     members=request.user)

    tag_list = tags.split("+")
    thread_queryset = Thread.objects.filter(content_type__pk=ctype.id,
                                            object_id=model_object.id)

    queryset = TaggedItem.objects.get_intersection_by_model(thread_queryset, tag_list)
    tags = Tag.objects.usage_for_queryset(queryset, counts=True)

    selected_tags = []
    tag_url = ''
    for item in tag_list:
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)
        tag_url += item + "+"

    if isinstance(model_object, Group):
        extra_context = {'group': model_object,}

    elif isinstance(model_object, Project):
        extra_context = {'project': model_object,}

    extra_context['thread_tags'] = tags
    extra_context['tag_url'] = tag_url
    extra_context['selected_tags'] = selected_tags

    return list_detail.object_list(request,
                                   queryset=queryset,
                                   template_name='blmessage/list_model.html',
                                   template_object_name='thread',
                                   extra_context=extra_context)

@login_required
def add_edit_thread(request, model, object_slug, thread_id=None, template='blmessage/form_thread.html'):
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=object_slug, members=request.user)
    ctype = ContentType.objects.get_for_model(model_object)
    tags = Tag.objects.usage_for_queryset(Thread.objects.filter(content_type__pk=ctype.id,
                                                                object_id=model_object.id), counts=True)

    if isinstance(model_object, Group):
        redirect_reverse = 'group-thread-detail'
        extra_context = {'group': model_object}

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-thread-detail'
        extra_context = {'project': model_object}

    if not thread_id:
        form = ThreadForm(request.POST or None)
    else:
        form = EditThreadForm(request.POST or None,
                              instance=thread_id and Thread.objects.get(pk=thread_id,
                                                                        content_type__pk=ctype.id))

    if request.method == "POST" and form.is_valid():
        thread = form.save(model_object, request.user)
        form.save_m2m()
        if not thread_id:
            Tag.objects.update_tags(thread, model_object.slug)
            message = _("Thread '%(thread)s' has been created" % {'thread': thread.title })
            thread.create_activity(request.user, Activity.CREATE)
        else:
            message = _("Thread '%(thread)s' has been updated" % {'thread': thread.title })

        # Notification
        request.user.message_set.create(message=message)

        return HttpResponseRedirect(reverse(redirect_reverse,
                                            kwargs = {'object_slug': object_slug,
                                                      'thread_id': thread.id}))
    extra_context['tags'] = tags
    extra_context['form'] = form
    return direct_to_template(request,
                              template=template,
                              extra_context=extra_context)

@login_required
def delete_thread_for_model(request, model, object_slug, thread_id):
    """ Delete thread for the model """
    thread = get_object_or_404(Thread, pk=thread_id)
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=object_slug, members=request.user)

    if isinstance(model_object, Group):
        redirect_reverse = 'group-messages'

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-messages'

    if thread.messages.all()[0].author == request.user:
        thread.create_activity(request.user, Activity.DELETE)
        thread.delete()

        # Notification
        request.user.message_set.create(message=_("Thread '%(thread)s' has been deleted" % {'thread': thread.title }))

    return HttpResponseRedirect(reverse(redirect_reverse, kwargs = {'object_slug': object_slug}))

@login_required
def edit_message_for_model(request, model, object_slug, thread_id, message_id, template='blmessage/form_message.html'):
    """ Edit message inside thread """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=object_slug, members=request.user)
    ctype = ContentType.objects.get_for_model(model_object)
    thread = get_object_or_404(Thread, pk=thread_id)

    if isinstance(model_object, Group):
        redirect_reverse = 'group-thread-detail'
        extra_context = {'group': model_object}

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-thread-detail'
        extra_context = {'project': model_object}

    instance_data = Message.objects.get(pk=message_id, author=request.user)
    data = {'body': instance_data.body, }

    form = MessageForm(request.POST or None, instance=instance_data, initial=data)

    if request.method == "POST" and form.is_valid():
        message = form.save(thread, request.user)
        message.create_activity(request.user, Activity.UPDATE)

        # Notification
        request.user.message_set.create(message=_("Your message has been updated"))

        return HttpResponseRedirect(reverse(redirect_reverse,
                                            kwargs={'object_slug': object_slug,
                                                    'thread_id': thread.id}))
    extra_context['form'] = form
    return direct_to_template(request,
                              template=template,
                              extra_context=extra_context)

@login_required
def delete_message_for_model(request, model, object_slug, thread_id, message_id):
    """ Delete a message from the thread """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=object_slug, members=request.user)

    message = get_object_or_404(Message, pk=message_id, author=request.user)
    message.create_activity(request.user, Activity.DELETE)
    message.delete()

    # Notification
    request.user.message_set.create(message=_("Your message has been deleted"))

    if isinstance(model_object, Group):
        redirect_reverse = 'group-thread-detail'
        extra_context = {'group': model_object}

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-thread-detail'
        extra_context = {'project': model_object}

    try:
        thread = Thread.objects.get(pk=thread_id)
    except Thread.DoesNotExist:
         return HttpResponseRedirect(reverse('project-messages', kwargs = {'object_slug': object_slug}))
    else:
        return HttpResponseRedirect(reverse(redirect_reverse,
                                            kwargs = {'object_slug': object_slug,
                                                      'thread_id': thread_id}))

@login_required
def list(request, model=None, slug=None):
    """ List all threads for this user """
    if not model:
        models = [Project, Group]
    elif model in ['projects', 'groups']:
        models = [Project, ] if model == 'projects' else [Group, ]
    else: raise Http404

    all_threads = []
    all_ids = []
    for model in models:
        ctype = ContentType.objects.get_for_model(model)
        if not slug:
            object_ids = [id['id'] for id in model.objects.filter(members=request.user).values('id')]
        else:
            object_ids = [id['id'] for id in model.objects.filter(members=request.user, slug__iexact=slug).values('id')]

        threads = Thread.objects.filter(content_type__pk=ctype.id).filter(object_id__in=object_ids)
        # sort the threads
        all_threads.extend(threads)
        all_ids.extend(object_ids)

    all_threads = sorted(all_threads, key=lambda x: x.title.lower())

    queryset = Thread.objects.filter(Q(object_id__in=all_ids),
                                     Q(content_type__pk=14)|Q(content_type__pk=15))

    tags = Tag.objects.usage_for_queryset(queryset, counts=True)

    return direct_to_template(request,
                              template='blmessage/thread_list.html',
                              extra_context={'thread_list': all_threads,
                                             'thread_tags': tags})

@login_required
def detail(request, thread_id):
    """ Detail page of the thread """
    thread = get_object_or_404(Thread, pk=thread_id)
    model = thread.content_type.model_class()
    object = get_object_or_404(model, members=request.user, id=thread.object_id)

    form = MessageForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        message = form.save(thread, request.user)
        message.create_activity(request.user, Activity.COMMENT)

        return HttpResponseRedirect(reverse('message-detail',
                                            kwargs = {'thread_id': thread_id }))

    return direct_to_template(request,
                              template='blmessage/detail.html',
                              extra_context={'thread': thread,
                                             'form': form,
                                             'object': object,
                                             'model': model._meta.verbose_name})

@login_required
def edit_thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)

    if not thread_id:
        form = ThreadForm(request.POST or None)
    else:
        form = EditThreadForm(request.POST or None,
                              instance=thread_id and Thread.objects.get(pk=thread_id))

    if request.method == "POST" and form.is_valid():
        thread = form.save(thread, request.user)

        # Notification
        request.user.message_set.create(message=_("Thread '%(thread)s' has been updated" % {'thread': thread.title }))

        return HttpResponseRedirect(reverse('message-detail',
                                            kwargs = {'thread_id': thread.id}))

    return direct_to_template(request,
                              template='blmessage/form_thread.html',
                              extra_context={'form': form})

@login_required
def delete_thread(request, thread_id):
    """ Delete the thread """
    thread = get_object_or_404(Thread, pk=thread_id)

    if thread.messages.all()[0].author == request.user:
        thread.delete()

        # Notification
        request.user.message_set.create(message=_("Thread '%(thread)s' has been deleted" % {'thread': thread.title }))

    return HttpResponseRedirect(reverse('message-list'))


@login_required
def edit_message(request, thread_id, message_id):
    """ Edit selected message """
    thread = get_object_or_404(Thread, pk=thread_id)

    form = MessageForm(request.POST or None,
                       instance=message_id and Message.objects.get(pk=message_id, author=request.user))

    if request.method == "POST" and form.is_valid():
        message = form.save(thread, request.user)
        # Notification
        request.user.message_set.create(message=_("Your message has been updated"))

        return HttpResponseRedirect(reverse('message-detail',
                                            kwargs={'thread_id': thread.id}))

    return direct_to_template(request,
                              template='blmessage/form_message.html',
                              extra_context={'form': form})

@login_required
def delete_message(request, thread_id, message_id):
    """ Delete message """
    message = get_object_or_404(Message, pk=message_id, author=request.user)
    message.delete()

    # Notification
    request.user.message_set.create(message=_("Your message has been deleted"))

    return HttpResponseRedirect(reverse('message-detail',
                                        kwargs = {'thread_id': thread_id}))

@login_required
def tagged_threads(request, tags=None):
    """ Threads by tag """
    models = [Project, Group]

    all_ids = []
    for model in models:
        ctype = ContentType.objects.get_for_model(model)
        object_ids = [id['id'] for id in model.objects.filter(members=request.user).values('id')]

        # sort the threads
        all_ids.extend(object_ids)

    tag_list = tags.split("+")
    thread_queryset = Thread.objects.filter(Q(object_id__in=all_ids),
                                            Q(content_type__pk=14)|Q(content_type__pk=15))

    queryset = TaggedItem.objects.get_intersection_by_model(thread_queryset, tag_list)
    tags = Tag.objects.usage_for_queryset(queryset, counts=True)

    selected_tags = []
    tag_url = ''
    for item in tag_list:
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)
        tag_url += item + "+"

    return list_detail.object_list(request,
                                   queryset=queryset,
                                   template_name='blmessage/thread_list.html',
                                   template_object_name='thread',
                                   extra_context={'thread_tags': tags,
                                                  'tag_url': tag_url,
                                                  'selected_tags': selected_tags,})
