from django import template
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from busylissy.blmessage.models import Thread, Message
from busylissy.blprofile.templatetags.avatar import avatar
from busylissy.blactivity.models import Activity

register = template.Library()

@register.simple_tag
def avatars_in_thread(thread_id):
    """ Return all the avatars in the thread """
    thread = get_object_or_404(Thread, pk=thread_id)

    users = thread.messages.order_by("author").values("author").distinct()

    avatar_thread = ''
    for user in users:
        user = get_object_or_404(User, pk=user['author'])
        avatar_thread += '<img src="%s" alt="%s" title="%s" />' % (avatar(user, True), user.username, user.username)

    return avatar_thread

@register.simple_tag
def your_messages(project, user):
    """ Return count of new messages """
    project_type = ContentType.objects.get_for_model(project)
    
    message_count = Thread.objects.filter(content_type__pk=project_type.pk,
                                          object_id=project.id).exclude(seen_by=user).count()
    
    return message_count
                                      

    
