from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from solo.models import SingletonModel
from ckeditor.fields import RichTextField


class Contact(SingletonModel):
    phones = models.ManyToManyField('PhoneNumber',
                                    verbose_name=_('Телефоны'))
    email = models.OneToOneField('Email',
                                 verbose_name=_('Электронная почта'),
                                 null=True,
                                 on_delete=models.CASCADE)
    address = RichTextField(_('Адрес'))
    title_text = RichTextField(_('Текст вверху'))
    schedule = RichTextField(_('График'))
    footer_text = RichTextField(_('Текст снизу'))

    class Meta:
        verbose_name = _('Контакты')
        verbose_name_plural = _('Контакты')

    def __str__(self):
        return ' '.join([self.main_phone().number, self.email.email])

    def main_phone(self):
        return self.phones.get_queryset()[0]


class PhoneNumber(models.Model):
    number = models.CharField(_('Номер телефона'),
                              max_length=32)

    class Meta:
        verbose_name = _('Номер телефона')
        verbose_name_plural = _('Номера телефонов')

    def __str__(self):
        return self.number


class Response(models.Model):
    image = models.ImageField(_('Фото клиента'),
                              upload_to='clients_photos')
    name = models.CharField(_('Имя клиента'),
                            max_length=128)
    status = models.CharField(_('Статус клиента'),
                              max_length=64)
    text = models.TextField(_('Текст отзыва'))

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')

    def __str__(self):
        return ' '.join([self.name, self.status])


class Agreement(SingletonModel):
    image = models.ImageField(_('Картинка'),
                              upload_to='agreement_photo')
    text = models.TextField(_('Текст'))

    class Meta:
        verbose_name = _('Договор займа')
        verbose_name_plural = _('Договор займа')

    def __str__(self):
        return mark_safe(self.text)


class Email(models.Model):
    email = models.EmailField(_('Электронная почта'),
                              max_length=64)
    active = models.BooleanField(_('Активная Почта, используемая при '
                                   'отправке писем "напишите нам"'),
                                 default=False,
                                 help_text=_('Будет использоваться только '
                                             'первая из активных почт'))
    
    class Meta:
        verbose_name = _('Электронная почта')
        verbose_name_plural = _('Электронные почты')

    def __str__(self):
        return self.email

