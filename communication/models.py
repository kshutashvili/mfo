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


class HotLinePhone(SingletonModel):
    number = models.CharField(_('Номер телефона'),
                              max_length=64)
    schedule_start = models.TimeField(_('Время активности, начиная с:'),
                                      null=True)
    schedule_end = models.TimeField(_('Время активности, заканчивая в:'),
                                    null=True)

    class Meta:
        verbose_name = _('Горячая линия')
        verbose_name_plural = _('Горячая линия')

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

    class Meta:
        verbose_name = _('Электронная почта')
        verbose_name_plural = _('Электронные почты')

    def __str__(self):
        return self.email


class WriteUsEmail(SingletonModel):
    email = models.OneToOneField('Email',
                                 verbose_name=_('Электронная почта'),
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Почта')
        verbose_name_plural = _('Почта для "Напишите нам"')

    def __str__(self):
        return self.email.email


class SocialNet(models.Model):
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Социальная сеть')
        verbose_name_plural = _('Социальные сети')

    def __str__(self):
        return self.link


class BlogItem(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    text = RichTextField(_('Текст статьи'))
    image = models.ImageField(_('Картинка'),
                              upload_to='blog_items')
    date = models.DateField(_('Дата анонса'))

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи в блоге')

    def __str__(self):
        return ' '.join([self.title, str(self.date)])


class LastArticles(SingletonModel):
    articles = models.ManyToManyField('BlogItem',
                                      verbose_name=_('Статьи'))

    class Meta:
        verbose_name = _('Последние статьи')
        verbose_name_plural = _('Блок последние статьи')

    def __str__(self):
        return 'Последние статьи'


FAQ_CATEGORY_ICON_CHOICES = (('general','Общие вопросы'),
                             ('execution','Оформление заявки'),
                             ('card','Банковская карта'),
                             ('credit','Кредитный договор'),
                             ('personal','Личный кабинет'),
                             ('credit_manipulation','Как погасить / увеличить кредит'))

class FaqCategory(models.Model):
    name = models.CharField(_('Название'),
                            max_length=128)
    icon = models.CharField(_('Иконка'),
                            max_length=64,
                            choices=FAQ_CATEGORY_ICON_CHOICES)
    faq_items = models.ManyToManyField('FaqItem')

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('FAQ категории')

    def __str__(self):
        return self.name


class FaqItem(models.Model):
    name = models.CharField(_('Название вопроса'),
                            max_length=255)
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Вопрос')
        verbose_name_plural = _('FAQ вопросы')

    def __str__(self):
        return self.name

