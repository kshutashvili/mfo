from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import format_html 

from solo.models import SingletonModel
from ckeditor.fields import RichTextField

from communication.models import Email, PhoneNumber, Response, SocialNet
from credit.models import CreditRateUp, CreditRate
from department.models import Department


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
        return ' '.join([self.title, 'ID:', str(self.id)])


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


class MenuHeaderItem(models.Model):
    name = models.CharField(_('Название пункта'),
                            max_length=128)
    order = models.PositiveIntegerField(_('Порядок'),
                                        default=0)
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))

    class Meta:
        verbose_name = _('Пункт меню')
        verbose_name_plural = _('Пункты меню в хедере')
        ordering = ['order',]

    def __str__(self):
        return self.name


class MenuHeaderBlock(SingletonModel):
    items = models.ManyToManyField('MenuHeaderItem',
                                   verbose_name=_('Пункты'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок меню в хедере')

    def __str__(self):
        return 'Блок'


class MenuFooterItem(models.Model):
    name = models.CharField(_('Название пункта'),
                            max_length=128)
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида html_id "
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
        return ' '.join([self.name, 'ID:', str(self.id)])


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
    credit_rates = models.ManyToManyField(CreditRate,
                                          verbose_name=_('Кредитные тарифы'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок кредитные тарифы на главной')

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


CLOSE_CREDIT_ICON_CHOICES = (('svg-phone','Терминал'),
                             ('svg-tablet','Личный кабинет'),
                             ('svg-house','Банк'))

class CloseCredit(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    text = models.TextField(_('Текст'))
    icon_class = models.CharField(_('Иконка'),
                                  max_length=128,
                                  choices=CLOSE_CREDIT_ICON_CHOICES) 
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
        return ' '.join(['Блок о безопасности', 'ID:', str(self.id)])


class SecurityItem(models.Model):
    text = RichTextField(_('Текст'))

    class Meta:
        verbose_name = _('Элемент безопасности')
        verbose_name_plural = _('Элементы безопасности на главной')

    def __str__(self):
        return mark_safe(self.text)


class DiscountStatic(SingletonModel):
    title = RichTextField(_('Заголовок'))
    image = models.ImageField(_('Картинка заднего фона'),
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


class AboutUsStatic(SingletonModel):
    title = models.CharField(_('Заголовок'),
                             max_length=64)
    subtitle = models.CharField(_('Подзаголовок'),
                                max_length=64)
    text = models.TextField(_('Текст'))
    advantages = models.ManyToManyField('Advantage',
                                        verbose_name=_('Преимущества'))
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))
    image = models.ImageField(_('Картинка'),
                              upload_to='about_us')
    middle_title = models.CharField(_('Заголовок на середине страницы'),
                                    max_length=128)
    middle_text = models.TextField(_('Текст на середине страницы'))
    responses = models.ManyToManyField(Response,
                                       verbose_name=_('Отзывы'))
    important_title = models.CharField(_('Заголовок важных аспектов'),
                                       max_length=128)
    important_aspects = models.ManyToManyField('ImportantAspect',
                                               verbose_name=_('Важные аспекты'))

    class Meta:
        verbose_name = _('Страница о нас')
        verbose_name_plural = _('Страница о нас')

    def __str__(self):
        return self.title


class ImportantAspect(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=64)
    text = models.TextField(_('Текст'))
    image = models.FileField(_('Картинка'),
                             upload_to='important_aspect',
                             null=True)

    class Meta:
        verbose_name = _('Аспект')
        verbose_name_plural = _('Важные аспекты')

    def __str__(self):
        return self.title


class MainPageTopBlockStatic(SingletonModel):
    title = models.CharField(_('Первая строка заголовка'),
                             max_length=128)
    subtitle = models.CharField(_('Вторая строка заголовка'),
                                max_length=128)
    footer = models.CharField(_('Подзаголовок'),
                              max_length=128)
    image = models.ImageField(_('Картинка на заднем фоне'),
                              upload_to='main_top_block')

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок вверху главной страницы')

    def __str__(self):
        return ' '.join([self.title, self.subtitle]) 


class MainPageStatic(SingletonModel):
    top_block = models.ForeignKey('MainPageTopBlockStatic',
                                  verbose_name=_('Верхний блок страницы'),
                                  on_delete=models.CASCADE)
    credits_up = models.ManyToManyField(CreditRateUp,
                                        verbose_name=_('Кредитные тарифы вверху страницы'))
    advantage = models.ForeignKey('AdvantageStatic',
                                  verbose_name=_('Блок преимущества'),
                                  on_delete=models.CASCADE)
    discount = models.ForeignKey('DiscountStatic',
                                 verbose_name=_('Блок акция'),
                                 on_delete=models.CASCADE,
                                 null=True)
    credit_block = models.ForeignKey('CreditRateStatic',
                                     verbose_name=_('Блок кредитные тарифы'),
                                     on_delete=models.CASCADE,
                                     null=True)
    credit_take = models.ManyToManyField('GetCredit',
                                         verbose_name=_('Блок как получить кредит'))
    security = models.ForeignKey('SecurityStatic',
                                 verbose_name=_('Блок о параметрах защиты'),
                                 on_delete=models.CASCADE,
                                 null=True)
    responses = models.ManyToManyField(Response,
                                       verbose_name=_('Блок отзывы'))
    departments = models.ManyToManyField(Department,
                                         verbose_name=_('Отделения'))
    credit_close = models.ForeignKey('CloseCreditStatic',
                                     verbose_name=_('Блок как закрыть кредит'),
                                     on_delete=models.CASCADE,
                                     null=True)
    credit_information = models.ForeignKey('CreditInformationBlockStatic',
                                           verbose_name=_('Блок информации о кредитах'),
                                           on_delete=models.CASCADE,
                                           null=True)
    menu_footer = models.ManyToManyField('MenuFooterBlock',
                                         verbose_name=_('Меню в футере'))
    social_nets = models.ManyToManyField(SocialNet,
                                         verbose_name=_('Социальные сети в футере'))

    class Meta:
        verbose_name = _('Главная страница')
        verbose_name_plural = _('Главная страница')

    def __str__(self):
        return 'Главная страница'


class IndexPageStatic(SingletonModel):
    advantage = models.ForeignKey('AdvantageStatic',
                                  verbose_name=_('Блок преимущества'),
                                  on_delete=models.CASCADE)
    discount = models.ForeignKey('DiscountStatic',
                                 verbose_name=_('Блок акция'),
                                 on_delete=models.CASCADE,
                                 null=True)
    credit_block = models.ForeignKey('CreditRateStatic',
                                     verbose_name=_('Блок кредитные тарифы'),
                                     on_delete=models.CASCADE,
                                     null=True)
    credit_take = models.ManyToManyField('GetCredit',
                                         verbose_name=_('Блок как получить кредит'))
    security = models.ForeignKey('SecurityStatic',
                                 verbose_name=_('Блок о параметрах защиты'),
                                 on_delete=models.CASCADE,
                                 null=True)
    responses = models.ManyToManyField(Response,
                                       verbose_name=_('Блок отзывы'))
    departments = models.ManyToManyField(Department,
                                         verbose_name=_('Отделения'))
    credit_close = models.ForeignKey('CloseCreditStatic',
                                     verbose_name=_('Блок как закрыть кредит'),
                                     on_delete=models.CASCADE,
                                     null=True)

    class Meta:
        verbose_name = _('Страница Партнерский лэндинг')
        verbose_name_plural = _('Страница Партнерский лэндинг')

    def __str__(self):
        return 'Страница Партнерский лэндинг'


class CreditInformation(models.Model):
    title = models.CharField(_('Заголовок'),
                             max_length=128)
    text = RichTextField(_('Текст'))

    class Meta:
        verbose_name = _('Информация по кредитам')
        verbose_name_plural = _('Информация по кредитам')

    def __str__(self):
        return self.title


class CreditInformationBlockStatic(SingletonModel):
    text = RichTextField(_('Текст'))
    information_items = models.ManyToManyField('CreditInformation',
                                               verbose_name=_('Блоки информации'))

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блок информации по кредитам на главной над футером')

    def __str__(self):
        return 'Блок'

