from modeltranslation.translator import register, TranslationOptions
from department import models


@register(models.Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('city', 'schedule')
    required_languages = ('ru', 'ua')

