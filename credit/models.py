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
    is_insurance = models.BooleanField(_('Страховка'),
                                       default=False)
    term_min = models.PositiveIntegerField(_('Минимальный срок кредита'))
    term_max = models.PositiveIntegerField(_('Максимальный срок кредита'))
    term_type = models.BooleanField(_('Тип срока кредита'),
                                    default=False,
                                    help_text=_('Если включено, то в месяцах '
                                                'Если отключено, то в неделях'))
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
    rate_file = models.FileField(_('Файл с процентами, формат .json'),
                                 upload_to='rates_files')

    class Meta:
        verbose_name = _('Кредитный тариф')
        verbose_name_plural = _('Кредитные тарифы')

    def __str__(self):
        return self.name

    def get_sum_min(self):
      return self.sum_min if not self.is_insurance else int(self.sum_min / 1.25)

    def get_sum_max(self):
      return self.sum_max if not self.is_insurance else int(self.sum_max / 1.25)

    def get_term_min_days(self):
        return self.term_min * 7

    def get_term_max_days(self):
        return self.term_max * 7


class PaymentTerm(models.Model):
    term = models.CharField(_('Платеж'),
                            max_length=128,
                            help_text=_('Пр. раз в месяц'))

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Сроки платежей')

    def __str__(self):
        return self.term


CREDIT_RATE_UP_CHOICES = (('cash','Наличка'),
                          ('stick-man','Пенсионер'),
                          ('sticker','Стикер'))

class CreditRateUp(models.Model):
    credit_rate = models.ForeignKey('CreditRate',
                                    verbose_name=_('Кредитный тариф'),
                                    on_delete=models.CASCADE)
    icon_class = models.CharField(_('Иконка'),
                                  max_length=128,
                                  choices=CREDIT_RATE_UP_CHOICES)

    class Meta:
        verbose_name = _('Популярный кредитный тариф')
        verbose_name_plural = _('Популярные кредитные тарифы, вверху на главной')

    def __str__(self):
        return self.credit_rate.name

