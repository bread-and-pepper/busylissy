from django import template
from django.utils.hashcompat import md5_constructor

register = template.Library()

@register.simple_tag
def rss_feed_token(feed, model_object):
    """ Return rss feed with token """
    salt = 'bltoken'

    if feed == "project":
        name = model_object.slug
    else: name = model_object.username
    
    token = md5_constructor(name + salt + str(model_object.pk))

    return '/feeds/%(feed)s/%(object)s/%(token)s/' % {'feed': feed,
                                                      'object': name,
                                                      'token': token.hexdigest() }
