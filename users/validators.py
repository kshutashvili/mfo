from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from content.helpers import clear_contact_phone


def mobile_phone_number(value):
    clean_phone = clear_contact_phone(value)

    if not len(clean_phone) == 12:
        raise ValidationError(
            _(u"Введите правильный номер телефона")
        )
