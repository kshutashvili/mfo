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
    amount = models.DecimalField(
        "Cумма платежа",
        max_digits=10,
        decimal_places=2
    )
    confirmed = models.BooleanField(
        "Подтвержден?",
        default=False
    )
    confirmed_dt = models.DateTimeField(
        "Дата заказа",
        blank=True,
        null=True
    )
    canceled = models.BooleanField(
        "Отменен?",
        default=False
    )
    cancel_dt = models.DateTimeField(
        "Дата отмены заказа",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Транзакция EasyPay'
        verbose_name_plural = 'Транзакции EasyPay'

    def __str__(self):
        return str(self.order_id)
