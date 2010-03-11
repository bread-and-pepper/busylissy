from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

class WMDEditor(forms.Textarea):

    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        if 'cols' not in attrs:
            attrs['cols'] = 58
        if 'rows' not in attrs:
            attrs['rows'] = 8
        super(WMDEditor, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        rendered = super(WMDEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            wmd_options = {
                output: "Markdown",
                buttons: "bold italic | link blockquote code image | ol ul"
            };
            </script>
            <script type="text/javascript" src="%swmd/wmd.js"></script>
            <div class="wmd-preview"></div>''' % settings.MEDIA_URL)
