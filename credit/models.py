from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.validators import MinValueValidator

from ckeditor.fields import RichTextField
from django_google_maps import fields as map_fields


class CreditRate(models.Model):
    name = models.CharField(_('Название тарифа'),
                            max_length=128)
    image = models.ImageField(_('Картинка'),
                              upload_to='credit_rate')
    sum_min = models.PositiveIntegerField(_('Минимальная сумма кредита'))
    sum_max = models.PositiveIntegerField(_('Максимальная сумма кредита'))
    term_min = models.PositiveIntegerField(_('Минимальный срок кредита, недель'))
    term_max = models.PositiveIntegerField(_('Максимальный срок кредита, недель'))
    rate_min = models.DecimalField(_('Минимальная ставка, %'),
                                   validators=[MinValueValidator(0.00)],
                                   decimal_places=2,
                                   max_digits=20)
    rate_max = models.DecimalField(_('Максимальная ставка, %'),
                                   validators=[MinValueValidator(0.00)],
                                   decimal_places=2,
                                   max_digits=20)
    payment_terms = models.ManyToManyField('PaymentTerm',
                                           verbose_name=_('Сроки платежей'))

    class Meta:
        verbose_name = _('Кредитный тариф')
        verbose_name_plural = _('Кредитные тарифы')

    def __str__(self):
        return self.name


class PaymentTerm(models.Model):
    term = models.CharField(_('Платеж'),
                            max_length=128,
                            help_text=_('Пр. раз в месяц'))

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Сроки платежей')

    def __str__(self):
        return self.term

