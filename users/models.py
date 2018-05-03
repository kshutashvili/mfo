from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

from users.utils import get_person_id
from users.validators import mobile_phone_number


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name=_('Пользователь'),
        on_delete=models.CASCADE
    )
    phone = models.CharField(
        validators=[mobile_phone_number, ],
        max_length=32,
        unique=True,
        verbose_name=_('Номер телефона')
    )
    two_authy = models.BooleanField(
        _('Двухфакторная аутентификация'),
        default=False
    )
    verify_code = models.CharField(
        _('Код подтверждения'),
        max_length=6,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Дополнительная информация')
        verbose_name_plural = _('Дополнительная информация')

    def __str__(self):
        return self.phone


class RequestPersonalArea(models.Model):
    name = models.CharField(
        "ФИО",
        max_length=256
    )
    birthday = models.DateField(
        "Дата рождения",
    )
    contract_num = models.CharField(
        "Номер договора",
        max_length=32
    )
    mobile_phone_number = models.CharField(
        "Номер телефона",
        max_length=32,
        validators=[mobile_phone_number, ]
    )
    turnes_person_id = models.CharField(
        "ID клиента в БД Turnes",
        max_length=32,
        blank=True
    )

    class Meta:
        verbose_name = _('Заявка на доступ в ЛК')
        verbose_name_plural = _('Заявки на доступ в ЛК')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        found_object = RequestPersonalArea.objects.filter(
            name=self.name,
            birthday=self.birthday,
            contract_num=self.contract_num,
            mobile_phone_number=self.mobile_phone_number
        ).exists()

        if found_object:
            return

        self.turnes_person_id = get_person_id(self.contract_num)

        super(RequestPersonalArea, self).save(*args, **kwargs)
