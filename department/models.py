from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField


class Department(models.Model):
    city = models.CharField(_('Город'),
                            max_length=128)
    address = models.CharField(_('Адрес'),
                            max_length=128)
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
        return ' '.join([self.city, self.address])

