from twilio.rest import Client

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.crypto import get_random_string
from django.conf import settings

from users.utils import get_person_id
from users.helpers import send_password
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

    turnes_person_id = models.IntegerField(
        "ID клиента в БД Turnes",
        blank=True,
        null=True
    )

    changed_default_password = models.BooleanField(
        "Стандартный пароль из sms был изменен",
        default=False
    )
    ready_for_turnes = models.BooleanField(
        "Анкета полностью заполнена",
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
        validators=[mobile_phone_number, ]
    )
    turnes_person_id = models.IntegerField(
        "ID клиента в БД Turnes",
        blank=True,
        null=True
    )
    has_account = models.BooleanField(
        "Создан аккаунт",
        default=False
    )
    message_sid = models.CharField(
        "Twillio message SID",
        max_length=64,
        blank=True
    )

    class Meta:
        verbose_name = _('Заявка на доступ в ЛК')
        verbose_name_plural = _('Заявки на доступ в ЛК')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # search previous Requests with current contract_num
        if RequestPersonalArea.objects.filter(contract_num=self.contract_num).exists():
            qs = RequestPersonalArea.objects.filter(contract_num=self.contract_num)
            self.has_account = qs[0].has_account
            qs.delete()

        # get Turnes ID for current contract_num
        self.turnes_person_id = get_person_id(
            contract_num=self.contract_num,
            phone=clear_contact_phone(self.mobile_phone_number)
        )
        print("turnes_person_id", self.turnes_person_id)
        if self.turnes_person_id and not self.has_account:
            self.has_account = self.create_user_after_request()

        super(RequestPersonalArea, self).save(*args, **kwargs)

    def create_user_after_request(self, *args, **kwargs):
        try:
            new_user = User.objects.create(
                first_name=self.name,
                mobile_phone=clear_contact_phone(self.mobile_phone_number),
                turnes_person_id=self.turnes_person_id
            )
        except Exception:
            return False
        new_user_password = get_random_string(length=8)
        new_user.set_password(new_user_password)
        new_user.save()
        print("new_user_password", new_user_password)
        try:
            m_sid = send_password(
                to=clear_contact_phone(self.mobile_phone_number),
                password=new_user_password
            )
        except Exception:
            new_user.delete()
            return False

        # m_sid = send_password(
        #     to="+380631280489",
        #     password=new_user_password
        # )
        if m_sid:
            self.message_sid = m_sid

        return True


class Questionnaire(models.Model):
    EMPTY_CHOICES = (('', ''),)
    user = models.OneToOneField(
        User,
        verbose_name=_('Пользователь'),
        on_delete=models.CASCADE,
        related_name='anketa',
        blank=True,
        null=True
    )
    # ----- step 1 fields -----
    last_name = models.CharField(
        _("Прізвище"),
        max_length=128,
        blank=True
    )
    first_name = models.CharField(
        _("Ім'я"),
        max_length=128,
        blank=True
    )
    middle_name = models.CharField(
        _("По батькові"),
        max_length=128,
        blank=True
    )
    birthday_date = models.DateField(
        _("Дата народження"),
        blank=True,
        null=True
    )
    mobile_phone = models.CharField(
        _("Контактний телефон"),
        max_length=30,
        validators=[mobile_phone_number, ],
        blank=True
    )
    email = models.EmailField(
        _("Email адрес"),
        blank=True
    )
    SEX_CHOICES = (
        ('male', 'Чоловік'),
        ('female', 'Жінка')
    )
    sex = models.CharField(
        "Стать",
        choices=SEX_CHOICES,
        max_length=10,
        blank=True
    )
    education = models.TextField(
        "Освіта",
        # choices=EMPTY_CHOICES,
        blank=True
    )
    marital_status = models.TextField(
        "Сімейний стан",
        # choices=EMPTY_CHOICES,
        blank=True
    )
    has_criminal_record = models.BooleanField(
        "Наявність судимості",
        default=False
    )
    itn = models.CharField(
        _("Індивідуальний податковий номер (ІПН)"),
        max_length=10,
        blank=True
    )
    passport_code = models.CharField(
        _("Серія та номер паспорта / Номер ID-картки"),
        max_length=9,
        blank=True
    )
    passport_date = models.DateField(
        _("Дата видачі паспорта"),
        blank=True,
        null=True
    )
    passport_outdate = models.DateField(
        _("Дійсний до (для ID карти)"),
        blank=True,
        null=True
    )
    passport_authority = models.CharField(
        _("Орган, що видав"),
        max_length=255,
        blank=True
    )
    registration_country = models.TextField(
        _("Країна"),
        blank=True
    )
    registration_state = models.TextField(
        _("Область (Регіон)"),
        blank=True
    )
    registration_district = models.TextField(
        _("Район"),
        blank=True
    )
    registration_city = models.TextField(
        _("Місто (СМТ, село)"),
        blank=True
    )
    registration_street = models.TextField(
        _("Вулиця (проспект, бульвар тощо)"),
        blank=True
    )
    registration_building = models.TextField(
        _("№ Будинку"),
        blank=True
    )
    registration_flat = models.TextField(
        _("№ Квартири"),
        blank=True
    )
    registration_index = models.TextField(
        _("Поштовий індекс"),
        blank=True
    )
    residence_country = models.TextField(
        _("Країна"),
        blank=True
    )
    residence_state = models.TextField(
        _("Область (Регіон)"),
        blank=True
    )
    residence_district = models.TextField(
        _("Район"),
        blank=True
    )
    residence_city = models.TextField(
        _("Місто (СМТ, село)"),
        blank=True
    )
    residence_street = models.TextField(
        _("Вулиця (проспект, бульвар тощо)"),
        blank=True
    )
    residence_building = models.TextField(
        _("№ Будинку"),
        blank=True
    )
    residence_flat = models.TextField(
        _("№ Квартири"),
        blank=True
    )
    residence_index = models.TextField(
        _("Поштовий індекс"),
        blank=True
    )
    # ----- end step 1 fields -----

    # ----- step 2 fields -----
    EMPLOYMENT_TYPE_CHOICES = (
        ('', 'Виберіть вид'),
        ('individual', 'Фізична особа'),
        ('entrepreneur', 'Фізична особа - підприємець (ФОП)'),
    )
    employment_type = models.TextField(
        "Вид зайнятості",
        choices=EMPLOYMENT_TYPE_CHOICES,
        blank=True
    )
    company_name = models.TextField(
        "Назва компанії",
        blank=True
    )
    edrpou_code = models.TextField(
        "ЄДРПОУ",
        blank=True
    )
    position = models.TextField(
        "Посада",
        blank=True
    )
    position_type = models.TextField(
        "Вид персоналу",
        # choices=EMPTY_CHOICES,
        blank=True
    )
    service_type = models.TextField(
        "Сфера діяльності",
        # choices=EMPTY_CHOICES,
        blank=True
    )
    company_experience = models.TextField(
        "Стаж роботи в компанії",
        blank=True
    )
    overall_experience = models.TextField(
        "Загальний трудовий стаж",
        blank=True
    )
    company_address = models.TextField(
        "Фактична адреса місця праці",
        blank=True
    )
    company_phone = models.TextField(
        "Контактний номер компанії",
        blank=True
    )
    labor_relations = models.TextField(
        "Трудові правовідносини",
        # choices=EMPTY_CHOICES,
        blank=True
    )
    # ФОП
    state_registration_date = models.TextField(
        "Дата державної реєстрації",
        blank=True
    )
    state_registration_authority = models.TextField(
        "Орган державної реєстрації",
        blank=True
    )
    activity_type = models.TextField(
        "Вид діяльності (КВЕД)",
        blank=True
    )
    confirmed_document = models.TextField(
        "Документ, що підтверджує державну реєстрацію",
        blank=True
    )
    EMPLOY_COUNT_CHOICES = (
        ('1-2', '1-2'),
        ('3-5', '3-5'),
        ('6-10', '6-10'),
        ('11', 'більше 10'),
    )
    employ_count = models.TextField(
        "Кількість співробітників",
        blank=True,
        choices=EMPLOY_COUNT_CHOICES
    )
    # ----- end step 2 fields -----

    # ----- step 3 fields -----
    bound_person_names = models.TextField(
        "ПІБ",
        blank=True
    )
    bound_person_itn = models.TextField(
        "Індивідуальний податковий номер (ІПН)",
        blank=True
    )
    bound_person_relationship = models.TextField(
        "Ступінь відносин",
        # choices=EMPTY_CHOICES,
        blank=True
    )
    bound_person_job = models.TextField(
        "Робота (Назва компанії, Адреса, Телефон тощо)",
        blank=True
    )
    bound_person_phone = models.TextField(
        "Контактний номер телефону",
        blank=True
    )
    bound_person_address = models.TextField(
        "Адреса фактичного проживання",
        blank=True
    )
    # ----- end step 3 fields -----
    # ----- step 4 fields -----
    salary = models.TextField(
        "Заробітна плата",
        blank=True
    )
    partner_salary = models.TextField(
        "Заробітна плата чоловіка/дружини",
        blank=True
    )
    bonuses = models.TextField(
        "Бонуси та премії",
        blank=True
    )
    social_benefits = models.TextField(
        "Соціальні пільги",
        blank=True
    )
    pension = models.TextField(
        "Пенсія",
        blank=True
    )
    partner_pension = models.TextField(
        "Пенсія чоловіка/дружини",
        blank=True
    )
    other_income = models.TextField(
        "Інший дохід",
        blank=True
    )
    overall_income = models.TextField(
        "Загальний дохід",
        blank=True
    )
    month_outgoing = models.TextField(
        "Щомісячні витрати",
        blank=True
    )
    month_loan_payments_outgoing = models.TextField(
        "Щомісячні платежі по кредитам",
        blank=True
    )
    other_outgoing = models.TextField(
        "Інші витрати",
        blank=True
    )
    dwelling_type = models.TextField(
        "Тип житла",
        blank=True
    )
    vehicle_count = models.IntegerField(
        "Кількість автомобілів",
        default=0
    )
    vehicle_description = models.TextField(
        "Опис авто (марка, модель тощо)",
        blank=True
    )
    # ----- end step 4 fields -----
    # ----- start step 5 fields -----
    credit_sum = models.TextField(
        "Сума кредиту",
        blank=True
    )
    credit_term = models.TextField(
        "Термін кредиту",
        blank=True
    )
    credit_period = models.TextField(
        "Періодичність оплати",
        blank=True
    )
    # ----- end step 5 fields -----
    blacklist = models.BooleanField(
        "В черном списке",
        default=False
    )

    class Meta:
        verbose_name = _('Анкета')
        verbose_name_plural = _('Анкеты')

    def __str__(self):
        return "Questionnaire"


class RegistrationCountry(models.Model):
    name = models.CharField(
        "Название",
        max_length=128
    )
    value = models.CharField(
        "Значение",
        max_length=128
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0
    )

    class Meta:
        ordering = ['order']
        verbose_name = _('Страна (для анкеты)')
        verbose_name_plural = _('Страны (для анкеты)')

    def __str__(self):
        return self.name
