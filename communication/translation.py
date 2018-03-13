from modeltranslation.translator import register, TranslationOptions
from communication import models


@register(models.BlogItem)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)
    required_languages = ('ua', 'ru')


@register(models.Agreement)
class AgreementTranslationOptions(TranslationOptions):
    fields = ('text', )
    required_languages = ('ua', 'ru')


@register(models.Contact)
class ContactTranslationOptions(TranslationOptions):
    fields = ('title', 'meta_title', 'meta_description', 'address',
              'schedule', 'title_text', 'footer_text')
    required_languages = ('ua', 'ru')


@register(models.FaqCategory)
class FaqCategoryTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('ua', 'ru')


@register(models.FaqItem)
class FaqItemTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('ua', 'ru')


@register(models.FaqPageStatic)
class FaqPageStaticTranslationOptions(TranslationOptions):
    fields = ('title', 'meta_title', 'meta_description')
    required_languages = ('ua', 'ru')


@register(models.BlogCategory)
class BlogCategoryOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('ua', 'ru')
