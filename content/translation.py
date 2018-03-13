from modeltranslation.translator import register, TranslationOptions
from content import models


@register(models.Spoiler)
class SpoilerTranslationOptions(TranslationOptions):
    fields = ('topic', 'content_left', 'content_right')
    required_languages = ('ua', 'ru')


@register(models.StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', )
    required_languages = ('ua', 'ru')


@register(models.MenuAboutItem)
class MenuAboutItemTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('ua', 'ru')


@register(models.MenuFooterItem)
class MenuFooterItemTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('ua', 'ru')


@register(models.MenuFooterBlock)
class MenuFooterBlockTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('ua', 'ru')


@register(models.MenuHeaderItem)
class MenuHeaderItemTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = ('ua', 'ru')


@register(models.JobStaticPage)
class JobStaticPageTranslationOptions(TranslationOptions):
    fields = ('text',)
    required_languages = ('ua', 'ru')


@register(models.GetCredit)
class GetCreditTranslationOptions(TranslationOptions):
    fields = ('text', 'title')
    required_languages = ('ua', 'ru')


@register(models.CreditRateStatic)
class CreditRateStaticTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
    required_languages = ('ua', 'ru')


@register(models.Advantage)
class TranslationOptions(TranslationOptions):
    fields = ('text',)
    required_languages = ('ua', 'ru')


@register(models.AdvantageStatic)
class AdvantageStaticTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
    required_languages = ('ua', 'ru')


@register(models.CloseCredit)
class CloseCreditTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
    required_languages = ('ua', 'ru')


@register(models.SecurityItem)
class SecurityItemTranslationOptions(TranslationOptions):
    fields = ('text',)
    required_languages = ('ua', 'ru')


@register(models.DiscountStatic)
class DiscountStaticTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
    required_languages = ('ua', 'ru')


@register(models.ImportantAspect)
class ImportantAspectTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
    required_languages = ('ua', 'ru')


@register(models.AboutUsStatic)
class AboutUsStaticTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'text', 'middle_title', 'middle_text',
              'important_title')
    required_languages = ('ua', 'ru')


@register(models.CreditInformation)
class CreditInformationTranslationOptions(TranslationOptions):
    fields = ('title', 'text')
    required_languages = ('ua', 'ru')


@register(models.CreditInformationBlockStatic)
class CreditInformationBlockStaticTranslationOptions(TranslationOptions):
    fields = ('text',)
    required_languages = ('ua', 'ru')


#@register(models.MainPageStatic)
#class MainPageStaticTranslationOptions(TranslationOptions):
#    fields = ('title', 'meta_title', 'meta_description')
#    required_languages = ('ua', 'ru')


#@register(models.CloseCreditStatic)
#class CloseCreditStaticTranslationOptions(TranslationOptions):
#    fields = ('title',)
#    required_languages = ('ua', 'ru')

