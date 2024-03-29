from solo.models import SingletonModel

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


# User = get_user_model()


class Payment(models.Model):
    RESERVED = "RESERVED"
    NEW = "NEW"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='payments',
        on_delete=models.CASCADE
    )

    account_id = models.IntegerField(
        "ID аккаунта в системе 4bill",
    )
    wallet_id = models.IntegerField(
        "ID кошелька в системе 4bill",
    )
    service_id = models.IntegerField(
        "ID сервиса в системе 4bill",
    )

    customer_ip_address = models.GenericIPAddressField(
        "IP-адрес пользователя",
        default="0.0.0.0"
    )

    amount = models.IntegerField(
        "Сумма оплаты"
    )
    amount_currency = models.CharField(
        "Валюта (формат ISO)",
        max_length=16,
        default="UAH"
    )
    tpp_id = models.BigIntegerField(
        "ID записи в таблице tpp БД turnes",
        blank=True,
        null=True
    )

    description = models.TextField(
        "Описание транзакции",
        blank=True
    )

    status = models.CharField(
        "Статус транзакции",
        max_length=32
    )
    is_paid = models.BooleanField(
        "Оплачен?",
        default=False
    )

    provider_transaction_id = models.IntegerField(
        "ID транзакции в системе 4bill",
        default=0
    )

    created_dt = models.DateTimeField(
        "Дата создания",
        auto_now_add=True
    )
    updated_dt = models.DateTimeField(
        "Дата последнего обновления",
        auto_now=True
    )

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return "Пользователь: {0}, Сумма: {1}, Статус: {2} ".format(
            self.user.id,
            self.amount,
            self.status
        )


class KeyFor4billAPI(SingletonModel):
    key = models.BigIntegerField(
        "Значение Key для 4bill API",
        default=20,
        help_text="Изменять можно только в том случае, если перестали работать запросы к API"
    )

    class Meta:
        verbose_name = 'Key для 4bill API'


class PaymentPrivat(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='privat_lk_pays',
        on_delete=models.CASCADE
    )
    tpp_id = models.BigIntegerField(
        "ID записи в таблице tpp БД turnes",
        blank=True,
        null=True
    )
    contract_num = models.CharField(
        "Номер договора",
        max_length=32
    )
    amount = models.DecimalField(
        "Сумма платежа",
        max_digits=10,
        decimal_places=2
    )
    created_dt = models.DateTimeField(
        "Дата создания",
        auto_now_add=True
    )
    updated_dt = models.DateTimeField(
        "Дата последнего обновления",
        auto_now=True
    )
