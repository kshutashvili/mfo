from django.contrib import admin

from credit import models


@admin.register(models.CreditRate)
class CreditRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'sum_min', 'sum_max', 'term_min', 'term_max',
                    'rate_min', 'rate_max')


@admin.register(models.PaymentTerm)
class PaymentTermAdmin(admin.ModelAdmin):
    list_display = ('term',)

