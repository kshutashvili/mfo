from django.db import models


class Bid(models.Model):
    contact_phone = models.CharField("Номер телефона",
                                     max_length=12,
                                     blank=True)
    city = models.CharField("Город",
                            max_length=64)
    name = models.CharField("Имя",
                            max_length=64,
                            blank=True)
    credit_sum = models.IntegerField("Сумма кредита",
                                     blank=True,
                                     null=True)
    termin = models.CharField("Срок кредита (к-ство недель/месяцев)",
                              max_length=32,
                              default='2')
    termin_type = models.CharField("Тип срока (неделя/месяц)",
                                   max_length=32,
                                   default="неделя")
    created_dt = models.DateTimeField("Дата создания",
                                      auto_now_add=True)
    updated_dt = models.DateTimeField("Дата изменения",
                                      auto_now=True)

    class Meta:
        verbose_name = "Заявки"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return "{} {}".format(self.city, self.credit_sum)
