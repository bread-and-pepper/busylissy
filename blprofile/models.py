from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from registration.signals import user_registered

import datetime

from stdimage import StdImageField

def avatar_upload(instance, filename):
    """ Upload the avatar to the correct directory """
    extension = filename.split('.')[-1]
    return 'avatars/%s.%s' % (instance.user.username,
                              extension)

class UserProfileManager(models.Manager):
    """ Extra functionality for a user profiles """

    def public(self):
        """ Returns only public profiles """
        return self.filter(is_public=True)

    def profile_callback(self, user, *args, **kwargs):
        """
        Creates user profile while registering new user
        registration/urls.py

        """
        new_profile = UserProfile.objects.create(user=user,)

class UserProfile(models.Model):
    """
    Defines the extra information that users can have on the site

    """
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )
    user = models.ForeignKey(User, unique=True)
    objects = UserProfileManager()
   
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.CharField(_('website'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    about_me = models.TextField(_('about me'), blank=True)
    notifications = models.BooleanField(_('notifications'), default=True, help_text=_('I want to receive notifications of activities in my projects'))
    language = models.CharField(_('language'), choices=settings.LANGUAGES, blank=True, null=True, max_length=80)
    is_public = models.BooleanField(_('is public'), help_text=_('Profile is visible for others.'))
           

    avatar = StdImageField(_('avatar'),
                           upload_to=avatar_upload,
                           blank=True,
                           size=(settings.AVATAR_SIZE, settings.AVATAR_SIZE, True),
                           thumbnail_size=(settings.AVATAR_THUMBNAIL_SIZE,
                                           settings.AVATAR_THUMBNAIL_SIZE, True))
    
    def __unicode__(self):
        return 'Profile for %s' % self.user.username
    
    @property
    def age(self):
        d = datetime.date.today()
        if self.birth_date:
            return (d.year - self.birth_date.year) \
                    - int((d.month, d.day) \
                    < (self.birth_date.month, self.birth_date.day))
        else: return None

    @models.permalink
    def get_absolute_url(self):
        return ('profile-detail', (), { 'username': self.user.username })

user_registered.connect(UserProfile.objects.profile_callback)
