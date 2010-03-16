from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete

from busylissy import blactivity
from tagging.fields import TagField

class Thread(models.Model):
    """ A thread is the aggregation of the messages """
    title = models.CharField(_("title"), max_length=100)
    closed = models.BooleanField(_("closed"), blank=True, default=False)
    latest_message_time = models.DateTimeField(_("latest message time"), blank=True, null=True)
    message_count = models.IntegerField(_('total amount of messages'), default=0)
    
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')
    seen_by = models.ManyToManyField(User, blank=True, null=True, related_name='seen_by')

    tags = TagField()

    valid_actions = ['created', 'deleted']
    
    def __unicode__(self):
        return "%s" % self.title
    
    @models.permalink
    def get_absolute_url(self):
        model_object = self.content_type.get_object_for_this_type(pk=self.object_id)
        return ('project-thread-detail', [model_object.slug, str(self.id)])

    class Meta:
        ordering = ('-latest_message_time', )
        verbose_name = _('thread')
        verbose_name_plural = _('threads')

class Message(models.Model):
    """ Messages are the content of a thread """
    thread = models.ForeignKey(Thread, related_name='messages')
    author = models.ForeignKey(User, related_name='forum_post_set')
    body = models.TextField(_("body"))
    created_at = models.DateTimeField(_("created_at"),
                                      blank=True,
                                      null=True,
                                      auto_now_add=True)

    valid_actions = ['commented on', 'updated', 'deleted']
    
    def save(self, force_insert=False, force_update=False):
        """ 
        When saving a message, the ``latest_message_time`` of a Thread should be
        updated. Also the count be refreshed.
        
        """
        super(Message, self).save(force_insert, force_update)
        
        # Update thread
        t = self.thread
        t.latest_message_time = t.messages.latest('created_at').created_at
        t.message_count = t.messages.count()
        t.save()

    def delete(self):
        """
        Removing a message should also reflect on the message count and latest
        message date in the Thread.

        Also when deleting the last post in the thread. The thread itself
        should be removed.

        """
        t = self.thread
        try:
            latest_message = Message.objects.exclude(pk=self.id).filter(thread=t.pk).latest('created_at')
            latest_message_time = latest_message.created_at
            
            # Update the thread
            t.message_count = t.messages.exclude(pk=self.id).count()
            t.latest_message_time = latest_message_time
            t.save()
        except Message.DoesNotExist:
            # Remove empty thread
            t.delete()
        super(Message, self).delete()

    class Meta:
        ordering = ('created_at',)
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        
    def __unicode__(self):
        return "%s" % self.id

blactivity.register(Thread)
blactivity.register(Message)
