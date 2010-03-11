from django import template
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.hashcompat import md5_constructor
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist

import urllib

GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "http://www.gravatar.com/")

register = template.Library()

class ProfileAvatarNotFound(Exception):
    message = "User has no avatar in it's profile."

def get_user(user):
    """ 
    Fetches the user, if it's not a user instance, tries to get the user by
    it's username 
    
    """
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise Exception, "Bad user supplied for avatar."
    return user

def get_profile_avatar(user, thumbnail):
    """ Returns the avatar if the user has supplied one in it's profile """
    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        raise ProfileAvatarNotFound()
    else:
        if not profile.avatar:
            raise ProfileAvatarNotFound()
        else:
            return profile.avatar.url if not thumbnail else profile.avatar.thumbnail.url()

def get_gravatar(user, size):
    """ Gets the gravatar avatar if it exists. Else returns default """
    url = "%savatar/%s/?" % (GRAVATAR_URL_PREFIX, md5_constructor(user.email).hexdigest())
    if size == settings.AVATAR_SIZE:
        default = settings.MEDIA_URL + '/avatars/default/male.png'
    else:
        default = settings.MEDIA_URL + '/avatars/default/male.thumbnail.png'
    url += urllib.urlencode({"s": str(size), "default": default})
    return escape(url)

def avatar(user, thumbnail=False):
    user = get_user(user)
    try:
        avatar = get_profile_avatar(user, thumbnail)
    except ProfileAvatarNotFound:
        size = settings.AVATAR_SIZE if not thumbnail else settings.AVATAR_THUMBNAIL_SIZE
        avatar = get_gravatar(user, size)
    return avatar

register.simple_tag(avatar)
