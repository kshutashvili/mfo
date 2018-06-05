from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator

from solo.models import SingletonModel
from ckeditor.fields import RichTextField
from PIL import Image

from vacancy.models import Vacancy
from users.models import Profile


class Contact(SingletonModel):
    title = models.CharField(_('Title страницы'),
                             max_length=255,
                             null=True)
    meta_title = models.CharField(_('Meta title страницы'),
                                  max_length=255,
                                  null=True)
    meta_description = RichTextField(_('Meta description страницы'),
                                     null=True)
    phones = models.ManyToManyField('PhoneNumber',
                                    verbose_name=_('Телефоны'))
    email = models.OneToOneField('Email',
                                 verbose_name=_('Электронная почта'),
                                 null=True,
                                 on_delete=models.CASCADE)
    address = RichTextField(_('Адрес'))
    title_text = RichTextField(_('Текст вверху'))
    schedule = RichTextField(_('График'))
    to_email = models.OneToOneField('Email',
                                    verbose_name=_('Электронная почта '
                                                   'для напишите нам'),
                                    null=True,
                                    on_delete=models.CASCADE,
                                    related_name='to_email')
    footer_text = RichTextField(_('Текст снизу'))
    success_form = models.ForeignKey('SuccessFormStatic',
                                     verbose_name=_('Форма при успешной '
                                                    'отправке сообщения'),
                                     on_delete=models.CASCADE,
                                     null=True)

    class Meta:
        verbose_name = _('Контакты')
        verbose_name_plural = _('Контакты')

    def __str__(self):
        return 'Контакты'

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
    text = models.TextField(_('Текст отзыва'),
                            max_length=1000)

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')

    def __str__(self):
        return ' '.join([self.name, self.status])


class Email(models.Model):
    email = models.EmailField(_('Электронная почта'),
                              max_length=64)

    class Meta:
        verbose_name = _('Электронная почта')
        verbose_name_plural = _('Электронные почты')

    def __str__(self):
        return self.email


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

    def save(self):
        super(BlogItem, self).save()
        if not self.image:
            return
        image = Image.open(self.image)
        (width, height) = image.size
        factor = max(width,height)
        if factor > 2000:
            k_factor = 2000./factor
            size = (int(width * k_factor), int(height * k_factor))
            image = image.resize(size, Image.ANTIALIAS)
            image.save(self.image.path)


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


class FaqPageStatic(SingletonModel):
    title = models.CharField(_('Title страницы'),
                             max_length=255,
                             null=True)
    meta_title = models.CharField(_('Meta title страницы'),
                                  max_length=255,
                                  null=True)
    meta_description = RichTextField(_('Meta description страницы'),
                                     null=True)
    faq_categories = models.ManyToManyField('FaqCategory',
                                            verbose_name=_('Категории с вопросами'))

    class Meta:
        verbose_name = _('Страница')
        verbose_name_plural = _('FAQ страница')

    def __str__(self):
        return 'FAQ страница'


class BlogCategory(models.Model):
    name = models.CharField(_('Название категории'),
                            max_length=128)
    link = models.CharField(_('URL-адрес'),
                            max_length=255,
                            help_text=_("Используйте ссылку вида /#html_id "
                                        "для блока лэндинга. Остальные ссылки "
                                        "указывать полностью (https://...)"))
    blog_items = models.ManyToManyField('BlogItem',
                                        verbose_name=_('Статьи'))

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории в блоге')

    def __str__(self):
        return self.name


class Resume(models.Model):
    first_name = models.CharField(_('Имя'),
                                  max_length=128)
    last_name = models.CharField(_('Фамилия'),
                                 max_length=128)
    city = models.CharField(_('Населенный пункт'),
                            max_length=128)
    vacancy = models.ForeignKey(Vacancy,
                                verbose_name=_('Вакансия'),
                                on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+{0,1}\d{9,15}$',
                                 message=_("Неправильный формат телефона: "))
    phone = models.CharField(_('Номер телефона'),
                             max_length=32,
                             validators=[phone_regex])
    email = models.EmailField(_("Электронная почта"))
    file = models.FileField(_('Резюме'),
                            upload_to='resume_files')

    class Meta:
        verbose_name = _('Резюме')
        verbose_name_plural = _('Резюме')

    def __str__(self):
        return ' '.join([self.first_name, self.last_name, self.vacancy.name])


class SuccessFormStatic(models.Model):
    title = models.CharField(_('Заголовок формы'),
                             max_length=128)
    text = models.TextField(_('Текст формы'),
                            max_length=400)
    extra_text = models.CharField(_('Дополнительный текст в левом нижнем '
                                    'углу'),
                                  max_length=255)

    class Meta:
        verbose_name = _('Форма успешно выполненного действия')
        verbose_name_plural = _('Формы успешно выполненного действия')

    def __str__(self):
        return self.title


class UserExistMessage(SingletonModel):
    page = models.OneToOneField('SuccessFormStatic',
                                verbose_name=_('Форма'),
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Форма')
        verbose_name_plural =_('Форма, если пользователь уже зарегестрирован')

    def __str__(self):
        return 'Форма'


class QuestionConfig(SingletonModel):
    name = models.CharField(_('От этого имени будут поститься комментарии '
                              'к вопросам в ЛК'),
                            max_length=128)
    message = models.TextField(_('Сообщение, завершающее закрытые вопросы'),
                               max_length=1200)

    class Meta:
        verbose_name = _('Конфигурация')
        verbose_name_plural = _('Конфигурация ответов в ЛК')

    def __str__(self):
        return self.name


class QuestionComment(models.Model):
    created_at = models.DateTimeField(_('Дата комментария'),
                                      auto_now_add=True)
    content = models.TextField(_('Комментарий'),
                               max_length=1200)
    is_admin = models.BooleanField(_('От администрации'),
                                   default=False)

    class Meta:
        verbose_name = _('Комментарий к вопросу пользователя')
        verbose_name_plural = _('Комментарии к вопросам пользователя')
        ordering = ['created_at',]

    def __str__(self):
        return str(self.content)


class UserQuestion(models.Model):
    is_closed = models.BooleanField(_('Вопрос закрыт'),
                                    default=False)
    user = models.ForeignKey(Profile,
                             verbose_name=_('Пользователь'),
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    created_at = models.DateTimeField(_('Дата создания вопроса'),
                                      auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления вопроса'),
                                      auto_now=True)
    content = models.TextField(_('Вопрос'),
                               max_length=1200)
    file = models.FileField(_('Прикрепленный файл'),
                            upload_to='questions_files',
                            null=True,
                            blank=True)
    comments = models.ManyToManyField('QuestionComment',
                                      verbose_name=_('Комментарии'),
                                      blank=True)
    end_message = models.ForeignKey('QuestionComment',
                                    verbose_name=_('Завершающий ответ'),
                                    on_delete=models.CASCADE,
                                    related_name='end',
                                    blank=True,
                                    null=True)
    # choices : 'read', '!read', 'force read'
    is_read = models.CharField(_('Прочитан'),
                               max_length=10,
                               default='read')

    class Meta:
        verbose_name = _('Вопрос пользователя')
        verbose_name_plural = _('Вопросы пользователей')
        ordering = ['-updated_at',]

    def __str__(self):
        if self.user:
            return ' | '.join([self.user.phone, self.content])
        else:
            return self.content


class CallbackSuccessForm(SingletonModel):
    success = models.ForeignKey('SuccessFormStatic',
                                verbose_name=_('Форма успешного заказа'),
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Форма')
        verbose_name_plural =_('Форма после успешного заказа звонка')

    def __str__(self):
        return self.success.title


SOCIAL_NETS_ICONS_CLASSES = (('twitter', 'Twitter'),
                             ('pinterest', 'Pinterest'),
                             ('linkedin', 'LinkedIn'),
                             ('facebook', 'Facebook'))

class SocialNetUnderHeader(models.Model):
    link = models.CharField(_('URL-адрес'),
                            max_length=255)
    image = models.CharField(_('Иконка'),
                             max_length=25,
                             choices=SOCIAL_NETS_ICONS_CLASSES)

    class Meta:
        verbose_name = _('Социальная сеть')
        verbose_name_plural = _('Социальные сети под хедером')

    def __str__(self):
        return self.link

