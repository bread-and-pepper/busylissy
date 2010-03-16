from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import get_model
from django.views.generic import list_detail
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404

from tagging.models import Tag, TaggedItem
from tagging.views import tagged_object_list

from busylissy.blproject.models import Project
from busylissy.blgroup.models import Group
from busylissy.blcontact.models import Contact
from busylissy.blcontact.forms import ContactForm
from busylissy.blcontact.decorators import get_contact

@login_required
def list_for_model(request, model, slug, template='blcontact/contact_list.html'):
    """ Returns the contacts for a model """
    model = get_model(*model.split('.'))
    q = model.objects.filter(members=request.user)
    object = get_object_or_404(model, slug=slug)

    if isinstance(object, Group):
        extra = {'group': object}
    elif isinstance(object, Project):
        extra = {'project': object}
    
    return list_detail.object_detail(request,
                                     queryset=q,
                                     slug=slug,
                                     template_name=template,
                                     extra_context=extra)

@login_required
def detail_for_model(request, model, model_slug, contact_slug, template='blcontact/detail.html'):
    """ Returns the details for a contact """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=model_slug)
    model_type = ContentType.objects.get_for_model(model_object)
    
    q = Contact.objects.filter(content_type__pk=model_type.id,
                               object_id=model_object.id)

    if isinstance(model_object, Group):
        extra = {'group': model_object}
    elif isinstance(model_object, Project):
        extra = {'project': model_object}

    return list_detail.object_detail(request,
                                     queryset=q,
                                     slug=contact_slug,
                                     template_name=template,
                                     extra_context=extra) 

@login_required
def add_edit_for_model(request, model, model_slug, contact_slug=None, template='blcontact/includes/form.html'):
    """ Add/Edit contact """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=model_slug, members=request.user)
    model_type = ContentType.objects.get_for_model(model_object)  
    
    if isinstance(model_object, Group):
        redirect_reverse = 'group-contact-detail'
        extra_context = {'group': model_object}

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-contact-detail'
        extra_context = {'project': model_object}

    form = ContactForm(request.POST or None,
                       instance=contact_slug and Contact.objects.get(slug__iexact=contact_slug,
                                                                     content_type__pk=model_type.id))

    if request.method == "POST" and form.is_valid():
        contact = form.save(model_object)
            
        return HttpResponseRedirect(reverse(redirect_reverse,
                                            kwargs = {'model_slug': model_slug,
                                                      'contact_slug': contact.slug}))
    extra_context['form'] = form
    return direct_to_template(request,
                              template=template,
                              extra_context=extra_context)

@login_required
def delete_for_model(request, model, model_slug, contact_slug):
    """ Delete an existing contact """
    model = get_model(*model.split('.'))
    model_object = get_object_or_404(model, slug=model_slug, members=request.user)
    model_type = ContentType.objects.get_for_model(model_object) 

    contact = get_object_or_404(Contact, slug=contact_slug, content_type__pk=model_type.id)
    
    if isinstance(model_object, Group):
        redirect_reverse = 'group-contacts'

    elif isinstance(model_object, Project):
        redirect_reverse = 'project-contacts'

    contact.delete()
    return HttpResponseRedirect(reverse(redirect_reverse,
                                        kwargs = {'slug': model_slug}))
@login_required
def list(request, model=None, slug=None):
    """ List all the contacts for this user """
    if not model:
        models = [Project, Group]
    elif model in ['projects', 'groups']:
        models = [Project, ] if model == 'projects' else [Group, ]
    else: raise Http404
    
    all_contacts = []
    all_ids = []
    for model in models:
        ctype = ContentType.objects.get_for_model(model)
        if not slug:
            object_ids = [id['id'] for id in model.objects.filter(members=request.user).values('id')]
        else:
            object_ids = [id['id'] for id in model.objects.filter(members=request.user, slug__iexact=slug).values('id')]
        
        contacts = Contact.objects.filter(content_type__pk=ctype.id).filter(object_id__in=object_ids)
        # Sort the contacts
        all_contacts.extend(contacts)
        all_ids.extend(object_ids)
    
    all_contacts = sorted(all_contacts, key=lambda x: x.last_name.lower())

    queryset = Contact.objects.filter(Q(object_id__in=all_ids),
                                      Q(content_type__pk=14)|Q(content_type__pk=15))

    tags = Tag.objects.usage_for_queryset(queryset, counts=True)
    
    return direct_to_template(request,
                              template='blcontact/contact_list.html',
                              extra_context={'contact_list': all_contacts,
                                             'contact_tags': tags})

@login_required
def detail(request, id):
    """ Returns details about the contact """
    contact = get_object_or_404(Contact, pk=id)
    model = contact.content_type.model_class()
    object = get_object_or_404(model, members=request.user, id=contact.object_id)

    return direct_to_template(request,
                              template='blcontact/detail.html',
                              extra_context={'contact': contact,
                                             'object': object,
                                             'model': model._meta.verbose_name})

@login_required
def add_edit(request, id=None):
    """ Add/Edit contact """
    form = ContactForm(request.POST or None,
                       instance=id and Contact.objects.get(pk=id))
    
    if request.method == "POST" and form.is_valid():
        contact = form.save()

        return HttpResponseRedirect(reverse('contact-detail',
                                            kwargs = {'id': contact.id, }))
    return direct_to_template(request,
                              template='blcontact/includes/form.html',
                              extra_context={'form': form,})

@login_required
def delete(request, id):
    """ Delete the contact """
    contact = get_object_or_404(Contact, pk=id)
    model = contact.content_type.model_class()
    object = get_object_or_404(model, members=request.user, id=contact.object_id)
    
    if object:
        contact.delete()
        
    return HttpResponseRedirect(reverse('contact-list'))

@login_required
def tagged_contacts(request, tags=None):
    """ Contacts by tag """
    models = [Project, Group]

    all_ids = []
    for model in models:
        ctype = ContentType.objects.get_for_model(model)
        object_ids = [id['id'] for id in model.objects.filter(members=request.user).values('id')]

        all_ids.extend(object_ids)

    tag_list = tags.split("+")
    contact_queryset = Contact.objects.filter(Q(object_id__in=all_ids),
                                              Q(content_type__pk=14)|Q(content_type__pk=15))

    queryset = TaggedItem.objects.get_intersection_by_model(contact_queryset, tag_list)
    tags = Tag.objects.usage_for_queryset(queryset, counts=True)

    selected_tags = []
    for item in tag_list:
        name = Tag.objects.get(name=item)
        tags.remove(name)
        selected_tags.append(name)
        tag_url = item + '+'

    return list_detail.object_list(request,
                                   queryset=queryset,
                                   template_name='blcontact/contact_list.html',
                                   template_object_name='contact',
                                   extra_context={'contact_tags': tags,
                                                  'tag_url': tag_url,
                                                  'selected_tags': selected_tags})
