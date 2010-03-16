import os, string, ftplib, re, decimal
from time import strftime, gmtime

from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django import forms
from django.conf import settings
from busylissy.blfile.settings import *
from busylissy.blfile.functions import _get_path, _get_file_type, _get_filterdate, _sort_by_attr, _get_settings_var, _get_breadcrumbs, _url_join, _handle_file_upload, _redirect_to_path

from busylissy.blfile.templatetags.fb_tags import query_helper
from busylissy.blfile.forms import MakeDirForm, UploadForm, RenameForm, BaseUploadFormSet
from busylissy.blproject.models import Project

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

# Precompile regular expressions
filter_re = [ re.compile(THUMB_PREFIX, re.M) ]
for exp in EXCLUDE:
    filter_re.append(re.compile(exp))

class FileObject(object):
    def __init__(self, filename, path, selecttype=None):
        self.filename = filename
        self.filename_lower = filename.lower()
        self.path = path
        self.filesize = os.path.getsize(os.path.join(PATH_SERVER, path, filename))
        self.date = os.path.getmtime(os.path.join(PATH_SERVER, path, filename))
        self.filetype = _get_file_type(filename)
        if not selecttype or self.filetype in SELECT_FORMATS[selecttype.capitalize()]:
            self.selectable = True

    def icon_url(self):
        icon = "file_type_" + self.filetype_checked.lower() + ".gif"
        return u"%s%s" % (settings.MEDIA_URL+"img/icons/", icon)
    
    def _filetype_checked(self):
        if self.filetype == "Folder" and os.path.isdir(self.path_full()):
            return self.filetype
        elif self.filetype != "Folder" and os.path.isfile(self.path_full()):
            return self.filetype
        else:
            return ""
    filetype_checked = property(_filetype_checked)
        
    def path_full(self):
        return u"%s" % os.path.join(PATH_SERVER, self.path, self.filename)
    
    def path_relative(self):
        return u"%s" % self.path_full().replace(settings.MEDIA_ROOT, '').lstrip('/')
    
    def url_full(self):
        if self.filetype == "Folder":
            return u"%s" % _url_join(URL_WWW, self.path, self.filename)
        else:
            return u"%s%s" % (_url_join(URL_WWW, self.path), self.filename)
    
    def url_relative(self):
        return u"%s" % self.url_full().replace(settings.MEDIA_URL, '').lstrip('/')
    
    def url_save(self):
        if SAVE_FULL_URL:
            return self.url_full()
        else:
            return self.url_relative()
    
    def link(self):
        if self.filetype_checked == "Folder":
            return u"%s%s" % (_url_join(URL_ADMIN, self.path), self.filename)
        else:
            return u"%s%s" % (_url_join(URL_WWW, self.path), self.filename)
    
    def date_formatted(self):
        return u"%s" % strftime("%d-%m-%Y", gmtime(self.date))

    def image_dimensions(self):
        if self.filetype == 'Image':
            try:
                im = Image.open(os.path.join(PATH_SERVER, path, self.filename))
                return im.size
            except:
                pass
        else:
            return False
    
    def image_is_generated(self):
        if self.filetype == 'Image':
            return _is_image_version(self.filename)
        else:
            return False
    
    def folder_is_empty(self):
        if os.path.isdir(self.path_full()):
            if not os.listdir(self.path_full()):
                return True
            else:
                return False
        else:
            return False

@login_required
def list(request, project_slug, dir_name=None):
    """
    Show list of files on a server-directory.
    """
    project = get_object_or_404(Project, slug__iexact=project_slug, members=request.user)
    path = _get_path(dir_name, str(project.pk))
    query = request.GET
    
    # INITIAL VARIABLES
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'thumbs_total': 0, 'generator_total': 0, 'select_total': 0 }
    counter = {}
    for k,v in EXTENSIONS.iteritems():
        counter[k] = 0
        
    try:
        dir_list = os.listdir(os.path.join(PATH_SERVER, path))
    except OSError:
        raise Http404
    
    files = []
    for file in dir_list:

        # EXCLUDE FILES MATCHING THUMB_PREFIX OR ANY OF THE EXCLUDE PATTERNS
        filtered = file.startswith('.')
        for re_prefix in filter_re:
            if re_prefix.search(file):
                filtered = True
        if filtered:
            continue
        
        # only increment results_total if file is not filtered
        results_var['results_total'] += 1
        
        # CREATE FILEOBJECT
        fileobject = FileObject(file, path, request.GET.get('type', ''))
        
        # COUNTER/RESULTS
        if fileobject.filetype:
            counter[fileobject.filetype] += 1
        if fileobject.filetype == 'Image':
            results_var['thumbs_total'] += 1
        if fileobject.filetype != 'Folder':
            results_var['delete_total'] += 1
        elif fileobject.filetype == 'Folder' and fileobject.folder_is_empty():
            results_var['delete_total'] += 1
        
        # FILTER / SEARCH
        append = False
        if fileobject.filetype == request.GET.get('filter_type', fileobject.filetype) and _get_filterdate(request.GET.get('filter_date', ''), fileobject.date):
            append = True
        if request.GET.get('q') and not re.compile(request.GET.get('q').lower(), re.M).search(file.lower()):
            append = False
        
        # APPEND FILE_LIST
        if append:
            files.append(fileobject)
            results_var['results_current'] += 1
    
    # SORTING
    files = _sort_by_attr(files, request.GET.get('o', 'date'))
    if request.GET.get('ot') == "desc":
        files.reverse()

    return direct_to_template(request,
                              template='blfile/list.html',
                              extra_context={'dir': dir_name,
                                             'files': files,
                                             'results_var': results_var,
                                             'query': query,
                                             'counter': counter,
                                             'settings_var': _get_settings_var(),
                                             'breadcrumbs': _get_breadcrumbs(query, dir_name, project.slug, ''),
                                             'title': _(u'FileBrowser'),
                                             'root_path': URL_HOME,
                                             'project': project,})

@login_required
def mkdir(request, project_slug, dir_name=None):
    """
    Make directory
    """
    project = get_object_or_404(Project, slug__iexact=project_slug, members=request.user)
    path = _get_path(dir_name, str(project.pk))
    query = request.GET
    
    if request.method == 'POST':
        form = MakeDirForm(PATH_SERVER, path, request.POST)
        if form.is_valid():
            server_path = os.path.join(PATH_SERVER, path, form.cleaned_data['dir_name'].lower())
            try:
                os.mkdir(server_path)
                os.chmod(server_path, 0775)
                # MESSAGE & REDIRECT
                msg = _('The Folder %s was successfully created.') % (form.cleaned_data['dir_name'].lower())
                request.user.message_set.create(message=msg)
                # on redirect, sort by date desc to see the new directory on top of the list
                # remove filter in order to actually _see_ the new folder
                redirect = _redirect_to_path(path)
                if redirect:
                    return HttpResponseRedirect(reverse('file-folder-list', kwargs = {'project_slug': project.slug, 'dir_name': redirect}))
                else:
                    return HttpResponseRedirect(reverse('file-list', kwargs = {'project_slug': project.slug }))
            except OSError, (errno, strerror):
                if errno == 13:
                    form.errors['dir_name'] = forms.util.ErrorList([_('Permission denied.')])
                else:
                    form.errors['dir_name'] = forms.util.ErrorList([_('Error creating directory.')])
    else:
        form = MakeDirForm(PATH_SERVER, path)

    return direct_to_template(request,
                              template='blfile/makedir.html',
                              extra_context={'form': form,
                                             'query': query,
                                             'settings_var': _get_settings_var(),
                                             'breadcrumbs': _get_breadcrumbs(query, dir_name, project.slug, _(u'New Folder')),
                                             'title': _(u'New Folder'),
                                             'root_path': URL_HOME,
                                             'project': project,})

@login_required
def upload(request, project_slug, dir_name=None):
    """
    Multipe Upload.
    """
    
    from django.forms.formsets import formset_factory
    project = get_object_or_404(Project, slug__iexact=project_slug, members=request.user)
    path = _get_path(dir_name, str(project.pk))
    query = request.GET
    
    # PIL's Error "Suspension not allowed here" work around:
    # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
    if STRICT_PIL:
        from PIL import ImageFile
    else:
        try:
            from PIL import ImageFile
        except ImportError:
            import ImageFile
    ImageFile.MAXBLOCK = IMAGE_MAXBLOCK # default is 64k
    
    UploadFormSet = formset_factory(UploadForm, formset=BaseUploadFormSet, extra=5)
    if request.method == 'POST':
        formset = UploadFormSet(data=request.POST, files=request.FILES, path_server=PATH_SERVER, path=path)
        if formset.is_valid():
            for cleaned_data in formset.cleaned_data:
                if cleaned_data:
                    # UPLOAD FILE
                    _handle_file_upload(PATH_SERVER, path, cleaned_data['file'])
            # MESSAGE & REDIRECT
            msg = _('Upload successful.')
            request.user.message_set.create(message=msg)
            # on redirect, sort by date desc to see the uploaded files on top of the list
            # remove filter in order to actually _see_ the uploaded file(s)
            redirect = _redirect_to_path(path)
            if redirect:
                return HttpResponseRedirect(reverse('file-folder-list', kwargs = {'project_slug': project.slug, 'dir_name': redirect}))
            else:
                return HttpResponseRedirect(reverse('file-list', kwargs = {'project_slug': project.slug }))
    else:
        formset = UploadFormSet(path_server=PATH_SERVER, path=path)

    return direct_to_template(request,
                              template='blfile/upload.html',
                              extra_context={'formset': formset,
                                             'dir': dir_name,
                                             'query': query,
                                             'settings_var': _get_settings_var(),
                                             'breadcrumbs': _get_breadcrumbs(query, dir_name, project.slug, _(u'Upload')),
                                             'title': _(u'Select files to upload'),
                                             'root_path': URL_HOME,
                                             'project': project,})

@login_required
def delete(request, project_slug, dir_name=None):
    """
    Delete existing File/Directory.
        When trying to delete a directory, the directory has to be empty.
    """
    project = get_object_or_404(Project, slug__iexact=project_slug, members=request.user)
    path = _get_path(dir_name, str(project.pk))
    query = request.GET
    msg = ""
    
    if request.GET:
        if request.GET.get('filetype') != "Folder":
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                # DELETE FILE
                os.unlink(server_path)
                if request.GET.get('filetype') == "Image":
                    # DELETE THUMB
                    file_ext = request.GET.get('filename').split('.')[-1]
                    thumb_name = request.GET.get('filename').replace('.', '_') + '_100x100_crop_q85.' + file_ext
                    os.unlink(os.path.join(PATH_SERVER, path, thumb_name))

                # MESSAGE & REDIRECT
                msg = _('The file %s was successfully deleted.') % (request.GET.get('filename').lower())
                request.user.message_set.create(message=msg)
                redirect = _redirect_to_path(path)
                if redirect:
                    return HttpResponseRedirect(reverse('file-folder-list', kwargs = {'project_slug': project.slug, 'dir_name': redirect}))
                else:
                    return HttpResponseRedirect(reverse('file-list', kwargs = {'project_slug': project.slug }))
            except OSError:
                # todo: define error message
                msg = OSError
        else:
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                os.rmdir(server_path)
                
                # MESSAGE & REDIRECT
                msg = _('The directory %s was successfully deleted.') % (request.GET.get('filename').lower())
                request.user.message_set.create(message=msg)
                
                redirect = _redirect_to_path(path)
                if redirect:
                    return HttpResponseRedirect(reverse('file-folder-list', kwargs = {'project_slug': project.slug, 'dir_name': redirect}))
                else:
                    return HttpResponseRedirect(reverse('file-list', kwargs = {'project_slug': project.slug }))
            except OSError:
                # todo: define error message
                msg = OSError
    
    if msg:
        return HttpResponseRedirect(reverse('file-list', kwargs = {'project_slug': project.slug }))

@login_required
def rename(request, project_slug, dir_name=None, file_name=None):
    """
    Rename existing File/Directory.
    """
    project = get_object_or_404(Project, slug__iexact=project_slug, members=request.user)
    path = _get_path(dir_name, str(project.pk))
    query = request.GET
    
    if os.path.isfile(os.path.join(PATH_SERVER, path, file_name)): # file
        file_type = _get_file_type(file_name)
        file_extension = os.path.splitext(file_name)[1].lower()
    else:
        file_extension = ""
        file_type = ""
    
    if request.method == 'POST':
        form = RenameForm(PATH_SERVER, path, file_extension, request.POST)
        if form.is_valid():
            old_path = os.path.join(PATH_SERVER, path, file_name)
            new_path = os.path.join(PATH_SERVER, path, request.POST.get('name').lower() + file_extension)
            try:
                os.rename(old_path, new_path)
                # RENAME IMAGE VERSIONS? TOO MUCH MAGIC?
                
                # MESSAGE & REDIRECT
                msg = _('Renaming was successful.')
                request.user.message_set.create(message=msg)
                redirect = _redirect_to_path(path)
                if redirect:
                    return HttpResponseRedirect(reverse('file-folder-list', kwargs = {'project_slug': project.slug, 'dir_name': redirect }))
                else:
                    return HttpResponseRedirect(reverse('file-list', kwargs = {'project_slug': project.slug }))
            except OSError, (errno, strerror):
                form.errors['name'] = forms.util.ErrorList([_('Error.')])
    else:
        form = RenameForm(PATH_SERVER, path, file_extension)

    return direct_to_template(request,
                              template='blfile/rename.html',
                              extra_context={'form': form,
                                             'query': query,
                                             'file_extension': file_extension,
                                             'settings_var': _get_settings_var(),
                                             'breadcrumbs': _get_breadcrumbs(query, dir_name, project.slug, _(u'Rename')),
                                             'title': _(u'Rename "%s"') % file_name,
                                             'root_path': URL_HOME,
                                             'project': project,})


