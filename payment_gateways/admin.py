from django.contrib import admin

from .models import *


@admin.register(EasypayPayment)
class EasypayPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'account',
        'confirmed',
        'save_dt'
    )


@admin.register(City24Payment)
class City24PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'account',
        'confirmed',
        'save_dt'
    )


@admin.register(PrivatbankPayment)
class PrivatbankPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'contract_num',
        'amount',
        'save_dt'
    )
    date_hierarchy = 'save_dt'
    list_per_page = 200
