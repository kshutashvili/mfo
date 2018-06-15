from django import forms
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe


class AdminFileWidget(forms.FileInput):
    """A FileField Widget that shows secure file link"""
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            url = reverse('protected_media',
                          args=(value.instance.id, ))
            out = u'<a href="{}">{}</a><br />{} '
            output.append(out.format(url, _(u'Preview'), _(u'Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
