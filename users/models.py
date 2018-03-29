from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator


class Profile(models.Model):
    user = models.OneToOneField(User,
    							verbose_name=_('Пользователь'),
    							on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+{0,1}\d{9,15}$',
                                 message=_("Номер может быть введён в одном из форматов: "
                                          "+380111111111, 380111111111, "
                                          "80111111111, 0111111111"))
    phone = models.CharField(validators=[phone_regex],
                             max_length=16,
                             unique=True,
                             verbose_name=_('Номер телефона'))
    two_authy = models.BooleanField(_('Двухфакторная аутентификация'),
    								default=False)
    verify_code = models.CharField(_('Код подтверждения'),
    							   max_length=6,
    							   null=True,
    							   blank=True)

    class Meta:
        verbose_name = _('Дополнительная информация')
        verbose_name_plural = _('Дополнительная информация')

    def __str__(self):
        return self.phone

