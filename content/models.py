from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import format_html 

from solo.models import SingletonModel
from ckeditor.fields import RichTextField

from communication.models import Email, PhoneNumber


class Spoiler(models.Model):
    topic = models.CharField(_('Тема спойлера'),
                             max_length=64)
    content_left = RichTextField(_('Текст левой колонки')) 
    content_right = RichTextField(_('Текст правой колонки'))
    file = models.FileField(_('Файл'),
                            upload_to='spoiler_files',
                            null=True,
                            blank=True)

    class Meta:
        verbose_name = _('Спойлер')
        verbose_name_plural = _('Спойлеры')

    def __str__(self):
        return self.topic


class StaticPage(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    spoilers = models.ManyToManyField('Spoiler',
                                      verbose_name=_('Спойлеры'))
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_('Используйте ссылки вида: url'))

    class Meta:
        verbose_name = _('Статическая страница')
        verbose_name_plural = _('Статические страницы')

    def __str__(self):
        return self.title


class MenuAboutItem(models.Model):
    name = models.CharField(_('Название пункта'),
                            max_length=128)
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Пункт меню')
        verbose_name_plural = _('Пункты меню на странице "О нас"')

    def __str__(self):
        return self.name


class MenuFooterItem(models.Model):
    name = models.CharField(_('Название пункта'),
                            max_length=128)
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Пункт меню')
        verbose_name_plural = _('Пункты меню в футере')

    def __str__(self):
        return self.name


class MenuFooterBlock(models.Model):
    name = models.CharField(_('Название блока'),
                            max_length=128)
    items = models.ManyToManyField('MenuFooterItem',
                                   verbose_name=_('Пункты блока'))
    order = models.PositiveIntegerField(_('Порядок отображения'),
                                        default=0)

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блоки меню в футере')

    def __str__(self):
        return self.name


class JobStaticPage(SingletonModel):
    image = models.ImageField(_('Картинка'),
                              upload_to='job_page')
    text = RichTextField(_('Текст'))
    email = models.ForeignKey(Email,
                              verbose_name=_('Контактная почта'),
                              on_delete=models.CASCADE)
    phone = models.ForeignKey(PhoneNumber,
                              verbose_name=_('Контактный телефон'),
                              null=True,
                              blank=True,
                              on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Статический блок')
        verbose_name_plural = _('Статическая часть страницы Вакансии')

    def __str__(self):
        return 'Статический блок'


class GetCredit(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    text = models.TextField(_('Текст'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блоки "Как получить кредит на главной"')

    def __str__(self):
        return self.title


class CreditRateStatic(SingletonModel):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    text = models.TextField(_('Небольшой текст'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Статический блок кредитные тарифы на главной')

    def __str__(self):
        return self.title


class Advantage(models.Model):
    text = RichTextField(_('Текст'))
    image = models.FileField(_('Иконка'),
                             upload_to='advantages')

    class Meta:
        verbose_name = _('Преимущество')
        verbose_name_plural = _('Преимущества')

    def __str__(self):
        return mark_safe(self.text)


class AdvantageStatic(SingletonModel):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    text = models.TextField(_('небольшой текст'))
    advantages = models.ManyToManyField('Advantage',
                                        verbose_name=_('Преимущества'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок преимущества на главной')

    def __str__(self):
        return self.title


class CloseCredit(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    image = models.FileField(_('Картинка'),
                             upload_to='close_credit')
    text = models.TextField(_('Текст'))
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Способ закрытия кредита')
        verbose_name_plural = _('Способы закрытия кредита')

    def __str__(self):
        return self.title


class CloseCreditStatic(SingletonModel):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    close_credits = models.ManyToManyField('CloseCredit',
                                           verbose_name=_('Варианты закрытия'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок закрытия кредита на главной')

    def __str__(self):
        return self.title


class SecurityStatic(SingletonModel):
    image1 = models.FileField(_('Картинка первого партнера'),
                              upload_to='secutiry_block')
    image2 = models.FileField(_('Картинка второго партнера'),
                              upload_to='secutiry_block')
    image3 = models.FileField(_('Картинка третьего партнера'),
                              upload_to='secutiry_block')
    security_items = models.ManyToManyField('SecurityItem',
                                            verbose_name=_('Элементы безопасности'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок о безопасности на главной')

    def __str__(self):
        return 'Блок о безопасности'


class SecurityItem(models.Model):
    text = RichTextField(_('Текст'))

    class Meta:
        verbose_name = _('Элемент безопасности')
        verbose_name_plural = _('Элементы безопасности на главной')

    def __str__(self):
        return mark_safe(self.text)


class DiscountStatic(SingletonModel):
    title = RichTextField(_('Заголовок'))
    image = models.FileField(_('Картинка'),
                             upload_to='discount')
    text = RichTextField(_('Текст'))
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок скидка на главной')

    def __str__(self):
        return mark_safe(self.title)

