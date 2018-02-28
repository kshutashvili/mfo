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
							help_text=_('Используйте ссылки вида /url'))

	class Meta:
		verbose_name = _('Статическая страница')
		verbose_name_plural = _('Статические страницы')

	def __str__(self):
		return self.title

