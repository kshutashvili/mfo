from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField
from django_google_maps import fields as map_fields


class Department(models.Model):
    address = map_fields.AddressField(_('Адрес'),
                                      max_length=128)
    geolocation = map_fields.GeoLocationField(max_length=100,
                                              null=True)
    schedule = models.CharField(_('Режим работы'),
                                max_length=128)
    phone = models.CharField(_('Телефон'),
                             max_length=32)
    email = models.EmailField(_('Электронная почта'),
                              max_length=64)

    class Meta:
        verbose_name = _('Отделение')
        verbose_name_plural = _('Отделения')

    def __str__(self):
        return self.address if self.address else self.id

