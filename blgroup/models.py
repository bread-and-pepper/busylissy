from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from authority.models import Permission
from tagging.models import Tag
from tagging.fields import TagField

from busylizzy.blmessage.models import Thread

class Group(models.Model):
    name = models.CharField(_(u'name'), max_length=80, unique=True)
    slug = models.SlugField(_(u'slug'))
    members = models.ManyToManyField(User, verbose_name=_(u'members'), related_name='group_members')
    threads = generic.GenericRelation(Thread)
    tags = TagField()

    class Meta:
        verbose_name = _(u'group')
        verbose_name_plural = _(u'groups')

    @models.permalink
    def get_absolute_url(self):
        return ('group-detail', (), {'slug': self.slug,})

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """
        - Delete the objects tag
        - Delete the permissions
        """
        Tag.objects.update_tags(self, None)
        
        permissions = Permission.objects.filter(content_type=ContentType.objects.get_for_model(self), object_id=self.id)
        permissions.delete()

        super(Group, self).delete(*args, **kwargs)
