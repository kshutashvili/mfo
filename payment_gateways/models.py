from django.db import models


class Tcredits(models.Model):
    client_id = models.PositiveIntegerField("ID клиента (client_id)")
    suma = models.DecimalField(
        "Сумма кредита (suma)",
        max_digits=10,
        decimal_places=2
    )
    vnoska = models.DecimalField(
        "Платеж (vnoska)",
        max_digits=10,
        decimal_places=2
    )
    egn = models.PositiveIntegerField("ИНН (egn)")
    contract_num = models.PositiveIntegerField("Номер договора (contract_num)")

    class Meta:
        verbose_name = 'Turnes credit (test example of tcredits)'
        verbose_name_plural = 'Turnes credits (test example of tcredits)'

    def __str__(self):
        return str(self.contract_num)


class Tpersons(models.Model):
    name = models.CharField(
        "Имя клиента (name)",
        max_length=64
    )
    name2 = models.CharField(
        "Отчество клиента (name2)",
        max_length=64
    )
    name3 = models.CharField(
        "Фамилия клиента (name3)",
        max_length=64
    )
    egn = models.PositiveIntegerField("ИНН (egn)")

    class Meta:
        verbose_name = 'Turnes person (test example of tpersons)'
        verbose_name_plural = 'Turnes persons (test example of tpersons)'

    def __str__(self):
        return "{0} {1}. {2}.".format(
            self.name3,
            self.name[0].upper(),
            self.name2[0].upper(),
        )


class Tcash(models.Model):
    sum = models.DecimalField(
        "Сумма платежа (sum)",
        max_digits=10,
        decimal_places=2
    )
    note = models.CharField(
        "Примечание (note)",
        max_length=128
    )
    type = models.CharField(
        "Тип (in/out, type)",
        max_length=32
    )
    service_code = models.CharField(
        "ID платежа в системе PrivatBank",
        max_length=128
    )
    vreme = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Turnes cash (test example of tcredits)'
        verbose_name_plural = 'Turnes cash (test example of tcash)'

    def __str__(self):
        return self.note


class EasypayPayment(models.Model):
    service_id = models.IntegerField(
        "Номер EF в системе EasyPay"
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции EasyPay"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Транзакция EF (тип EasyPay)'
        verbose_name_plural = 'Транзакции EF (тип EasyPay)'

    def __str__(self):
        return str(self.order_id)


# Familniy bank
class City24Payment(models.Model):
    service_id = models.IntegerField(
        "Номер EF в системе Банк 'Фамільний'"
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции Банк 'Фамільний'"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция EF (Тип Банк Фамільний)"
        verbose_name_plural = "Транзакции EF (Тип Банк Фамільний)"

    def __str__(self):
        return str(self.order_id)


class PrivatbankPayment(models.Model):
    transaction_id = models.CharField(
        "ID транзакции (ПБ)",
        max_length=128,
        unique=True
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255
    )
    contract_num = models.CharField(
        "Номер договора",
        max_length=128
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    created_dt = models.DateTimeField(
        "Дата создания транзакции",
        blank=True,
        null=True
    )
    confirm_dt = models.DateTimeField(
        "Дата подтверждения транзакции",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция EF (тип PrivatBank)"
        verbose_name_plural = "Транзакции EF (тип PrivatBank)"

    def __str__(self):
        return self.transaction_id


class SkyEasypayPayment(models.Model):
    service_id = models.IntegerField(
        "Номер EF в системе EasyPay"
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции EasyPay"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Транзакция Sky (Тип EasyPay)'
        verbose_name_plural = 'Транзакции Sky (Тип EasyPay)'

    def __str__(self):
        return str(self.order_id)


# Familniy bank
class SkyCity24Payment(models.Model):
    service_id = models.IntegerField(
        "Номер EF в системе Банк 'Фамільний'"
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции Банк 'Фамільний'"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция Sky (Тип Банк Фамільний)"
        verbose_name_plural = "Транзакции Sky (Тип Банк Фамільний)"

    def __str__(self):
        return str(self.order_id)


class SkyPrivatbankPayment(models.Model):
    transaction_id = models.CharField(
        "ID транзакции (ПБ)",
        max_length=128,
        unique=True
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255
    )
    contract_num = models.CharField(
        "Номер договора",
        max_length=128
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    created_dt = models.DateTimeField(
        "Дата создания транзакции",
        blank=True,
        null=True
    )
    confirm_dt = models.DateTimeField(
        "Дата подтверждения транзакции",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция Sky (Тип PrivatBank)"
        verbose_name_plural = "Транзакции Sky (Тип PrivatBank)"

    def __str__(self):
        return self.transaction_id


# City24
class C24Payment(models.Model):
    service_id = models.IntegerField(
        "Номер EF в системе",
        default=25
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция EF (Тип City24)"
        verbose_name_plural = "Транзакции EF (Тип City24)"

    def __str__(self):
        return str(self.order_id)


# City24
class SkyC24Payment(models.Model):
    service_id = models.IntegerField(
        "Номер EF в системе",
        default=25
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция Sky (Тип City24)"
        verbose_name_plural = "Транзакции Sky (Тип City24)"

    def __str__(self):
        return str(self.order_id)


# Portmone (type Privat)
class PortmonePrivatPayment(models.Model):
    transaction_id = models.CharField(
        "ID транзакции (ПБ)",
        max_length=128,
        unique=True
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255
    )
    contract_num = models.CharField(
        "Номер договора",
        max_length=128
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    created_dt = models.DateTimeField(
        "Дата создания транзакции",
        blank=True,
        null=True
    )
    confirm_dt = models.DateTimeField(
        "Дата подтверждения транзакции",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция Sky (тип Portmone-Privat)"
        verbose_name_plural = "Транзакции Sky (тип Portmone-Privat)"

    def __str__(self):
        return self.transaction_id


# Portmone (type Easypay)
class PortmoneEasypayPayment(models.Model):
    service_id = models.IntegerField(
        "Сервисный номер EF"
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Транзакция Sky (тип Portmone-Easypay)'
        verbose_name_plural = 'Транзакции Sky (тип Portmone-Easypay)'

    def __str__(self):
        return str(self.order_id)


# Okcibank (type Privat)
class OkciPrivatPayment(models.Model):
    transaction_id = models.CharField(
        "ID транзакции (ПБ)",
        max_length=128,
        unique=True
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255
    )
    contract_num = models.CharField(
        "Номер договора",
        max_length=128
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    created_dt = models.DateTimeField(
        "Дата создания транзакции",
        blank=True,
        null=True
    )
    confirm_dt = models.DateTimeField(
        "Дата подтверждения транзакции",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Транзакция Okci (тип Privat)"
        verbose_name_plural = "Транзакции Okci (тип Privat)"

    def __str__(self):
        return self.transaction_id


# Okcibank (type Easypay)
class OkciEasypayPayment(models.Model):
    service_id = models.IntegerField(
        "Сервисный номер EF"
    )
    order_id = models.BigIntegerField(
        "Уникальный идентификатор транзакции"
    )
    account = models.CharField(
        "Идентификатор пользователя (№ договора)",
        max_length=128
    )
    client_name = models.CharField(
        "ФИО клиента",
        max_length=255,
        blank=True
    )
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    inrazpredelenie_id = models.CharField(
        "ID in_razpredelenie",
        max_length=128,
        blank=True
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены",
        blank=True,
        null=True
    )
    save_dt = models.DateTimeField(
        "Дата сохранения",
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Транзакция Okci (тип Easypay)'
        verbose_name_plural = 'Транзакции Okci (тип Easypay)'

    def __str__(self):
        return str(self.order_id)
