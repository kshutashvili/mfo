from django.db import models

from .fields import ProtectedFileField
# from .storages import ProtectedFileSystemStorage

# Create your models here.


class Customer(models.Model):
    cl_id = models.TextField(
        'Идентификатор клиента',
        blank=True
    )
    cl_id_text = models.TextField(
        'Статический текст подтверждения выдачи информации',
        blank=True
    )
    last_name = models.TextField(
        'Фамилия',
        blank=True
    )
    first_name = models.TextField(
        'Имя',
        blank=True
    )
    middle_name = models.TextField(
        'Отчество',
        blank=True
    )
    birth_day = models.TextField(
        'Дата рождения',
        blank=True
    )
    inn = models.TextField(
        'Идентификационный номер налогоплательщика',
        blank=True
    )
    phone = models.TextField(
        'Актуальный телефон',
        blank=True
    )
    email = models.TextField(
        'Email',
        blank=True
    )
    sex = models.TextField(
        'Пол',
        blank=True,
        help_text='(M - мужской, F - женский)'
    )
    resident = models.TextField(
        'Определение резидентности',
        blank=True,
        help_text='(UA — резидент, /UA — нерезидент)'
    )
    edrpou = models.TextField(
        'ЕДРПОУ',
        blank=True
    )
    signature = models.TextField(
        'Подпись SHA1',
        blank=True
    )
    type = models.TextField(
        'Тип',
        blank=True
    )
    date_modification = models.TextField(
        'Последняя дата модификации данных',
        blank=True
    )

    class Meta:
        verbose_name = "Клиенты (BankID)"
        verbose_name_plural = "Клиент (BankID)"

    def __str__(self):
        return str(self.id)


class Document(models.Model):
    customer = models.ForeignKey(
        Customer,
        related_name='documents',
        on_delete=models.CASCADE
    )
    issue = models.TextField(
        'Кем выдан',
        blank=True
    )
    number = models.TextField(
        'Номер',
        blank=True
    )
    series = models.TextField(
        'Серия',
        blank=True
    )
    issue_country_iso2 = models.TextField(
        'Cтрана выдачи',
        blank=True
    )
    date_issue = models.TextField(
        'Когда выдан',
        blank=True
    )
    date_expiration = models.TextField(
        'Cрок действия',
        blank=True
    )
    type = models.TextField(
        'Тип документа',
        blank=True,
        help_text='passport – гражданский паспорт; zpassport – загранпаспорт; ident – удостоверение личности'
    )
    date_modification = models.TextField(
        'Последняя дата модификации данных',
        blank=True
    )

    class Meta:
        verbose_name = "Документы (BankID)"
        verbose_name_plural = "Документ (BankID)"

    def __str__(self):
        return str(self.id)


class Address(models.Model):
    customer = models.ForeignKey(
        Customer,
        related_name='addesses',
        on_delete=models.CASCADE
    )
    country = models.TextField(
        'Страна',
        blank=True
    )
    state = models.TextField(
        'Область',
        blank=True
    )
    area = models.TextField(
        'Район',
        blank=True
    )
    city = models.TextField(
        'Город',
        blank=True
    )
    street = models.TextField(
        'Улица',
        blank=True
    )
    house_no = models.TextField(
        'Номер дома',
        blank=True
    )
    flat_no = models.TextField(
        'Номер квартиры',
        blank=True
    )
    type = models.TextField(
        'Тип адреса',
        blank=True,
        help_text='factual — адрес регистрации; birth – адрес рождения'
    )
    date_modification = models.TextField(
        'Последняя дата модификации данных',
        blank=True
    )

    class Meta:
        verbose_name = "Адреса (BankID)"
        verbose_name_plural = "Адрес (BankID)"

    def __str__(self):
        return str(self.id)


def get_user_image_folder(instance, filename):
    return "scans/inn%s/%s" % (instance.customer.inn, filename)


class ScanDocument(models.Model):
    customer = models.ForeignKey(
        Customer,
        related_name='scans',
        on_delete=models.CASCADE
    )
    file = ProtectedFileField(
        verbose_name='Файл скана',
        upload_to=get_user_image_folder,
        blank=True,
        null=True
    )
    link = models.TextField(
        'URL выкачки скана',
        blank=True
    )
    extension = models.TextField(
        'Тип расширения файла',
        blank=True
    )
    number = models.TextField(
        'Порядковый номер документа',
        blank=True
    )
    type = models.TextField(
        'Типы сканов',
        blank=True,
        help_text='passport — скан гражданского паспорта; zpassport — скан загранпаспорта; inn – скан идентификационного налогового номера\npersonalPhoto – фотография личности (анфас)'
    )
    date_create = models.TextField(
        'Дата сканирования',
        blank=True
    )
    date_modification = models.TextField(
        'Последняя дата модификации данных',
        blank=True
    )

    class Meta:
        verbose_name = "Сканы (BankID)"
        verbose_name_plural = "Скан (BankID)"

    def __str__(self):
        return str(self.id)
