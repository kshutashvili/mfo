from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from users.utils import get_person_id
from users.validators import mobile_phone_number
from users.managers import UserManager
from content.helpers import clear_contact_phone


class User(AbstractBaseUser, PermissionsMixin):
    # auth field
    mobile_phone = models.CharField(
        _('mobile phone'),
        unique=True,
        max_length=30,
        validators=[mobile_phone_number, ]
    )

    email = models.EmailField(
        _('email address'),
        blank=True
    )
    first_name = models.CharField(
        _('first name'),
        max_length=30,
        blank=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        blank=True
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        auto_now_add=True
    )
    is_active = models.BooleanField(
        _('active'),
        default=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    turnes_person_id = models.CharField(
        "ID клиента в БД Turnes",
        max_length=32,
        blank=True
    )

    changed_default_password = models.BooleanField(
        "Стандартный пароль из sms был изменен",
        default=False
    )

    objects = UserManager()

    USERNAME_FIELD = 'mobile_phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name


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
        validators=[mobile_phone_number, ],
        unique=True
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
        # search request object with particular
        found_object = RequestPersonalArea.objects.filter(
            contract_num=self.contract_num
        ).exists()

        if found_object:
            return

        print("CLEARING PHONE", clear_contact_phone(self.mobile_phone_number))
        self.turnes_person_id = get_person_id(
            contract_num=self.contract_num,
            phone=clear_contact_phone(self.mobile_phone_number)
        )

        super(RequestPersonalArea, self).save(*args, **kwargs)
