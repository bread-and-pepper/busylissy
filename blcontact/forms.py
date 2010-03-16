from django.forms import ModelForm
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

import re

from busylissy.blcontact.models import Contact

attrs_dict = {'class': 'required' }
alnum_re = re.compile(r'^\w+$')
alnum_space_re = re.compile(r'^[ \w]+$')

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ('slug', 'content_type', 'object_id')
    
    def save(self, object=None, force_insert=False, force_update=False, commit=True):
        contact = super(ContactForm, self).save(commit=False)

        if object:
            contact.content_type = ContentType.objects.get_for_model(object) 
            contact.object_id = object.id
            
        contact.slug = slugify("%s %s" % (contact.first_name, contact.last_name))

        if commit:
            contact.save()
        return contact
