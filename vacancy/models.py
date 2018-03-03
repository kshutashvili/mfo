from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from solo.models import SingletonModel
from ckeditor.fields import RichTextField


class Category(models.Model):
    name = models.CharField(_('Название категории'),
                            max_length=128)
    vacancies = models.ManyToManyField('Vacancy',
                                       verbose_name=_('Вакансии'))

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории вакансий')

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    name = models.CharField(_('Название вакансии'),
                            max_length=128)
    demands = RichTextField(_('Требования'))
    conditions = RichTextField(_('Условия'))

    class Meta:
        verbose_name = _('Вакансия')
        verbose_name_plural = _('Вакансии')

    def __str__(self):
        return self.name

