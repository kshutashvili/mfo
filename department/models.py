from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField
from django_google_maps import fields as map_fields


class Department(models.Model):
    city = models.CharField(_('Город'),
                            max_length=128,
                            null=True)
    address = map_fields.AddressField(_('Адрес [ru]'),
                                      max_length=128)
    address_ua = models.CharField(_('Адрес [ua]'),
                                  max_length=255,
                                  null=True)
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
        return self.address if self.address else str(self.id)

