from modeltranslation.translator import register, TranslationOptions
from credit import models


@register(models.CreditRate)
class CreditRateTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('ua', 'ru')


@register(models.PaymentTerm)
class PaymentTermTranslationOptions(TranslationOptions):
    fields = ('term',)
    required_languages = ('ua', 'ru')

