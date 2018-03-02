from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ckeditor.fields import RichTextField


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



