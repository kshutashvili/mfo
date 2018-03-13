from modeltranslation.translator import register, TranslationOptions
from vacancy import models


@register(models.Vacancy)
class VacancyTranslationOptions(TranslationOptions):
    fields = ('name', 'demands', 'conditions',)
    required_languages = ('ua', 'ru')


@register(models.Category)
class CategoryVacancyTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('ua', 'ru')

