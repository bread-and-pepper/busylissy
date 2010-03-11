from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from tagging.models import Tag

class Contact(models.Model):
    first_name = models.CharField(_(u'first name'), max_length=80)
    last_name = models.CharField(_(u'last name'), max_length=255)
    slug = models.SlugField(_('slug'))
    phone = models.CharField(_(u'phone'), max_length=13, blank=True)
    email = models.EmailField(_(u'email'), blank=True)
    extra = models.TextField(_(u'extra information'), blank=True)
    lead = models.BooleanField()
    tags = TagField()

    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    @models.permalink
    def get_absolute_url(self):
        model_object = self.content_type.get_object_for_this_type(pk=self.object_id)
        return ('project-contact-detail', [str(model_object.id), str(self.id)])

    class Meta:
        unique_together = (("first_name", "last_name", "content_type", "object_id"), ("slug", "content_type", "object_id"))

    def delete(self, *args, **kwargs):
        """ Delete tags for object """
        Tag.objects.update_tags(self, None)

        super(Contact, self).delete(*args, **kwargs)
