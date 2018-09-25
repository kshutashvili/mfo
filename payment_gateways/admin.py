from django.contrib import admin

from .models import *


@admin.register(EasypayPayment)
class EasypayPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'account',
        'amount',
        'confirmed',
        'save_dt'
    )
    search_fields = ('order_id', 'account', 'client_name')


@admin.register(City24Payment)
class City24PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'account',
        'amount',
        'confirmed',
        'save_dt'
    )
    search_fields = ('order_id', 'account', 'client_name')


@admin.register(PrivatbankPayment)
class PrivatbankPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'contract_num',
        'amount',
        'save_dt'
    )
    search_fields = ('contract_num', 'client_name')
    date_hierarchy = 'save_dt'
    list_per_page = 200


@admin.register(SkyEasypayPayment)
class SkyEasypayPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'account',
        'amount',
        'confirmed',
        'save_dt'
    )
    search_fields = ('order_id', 'account', 'client_name')


@admin.register(SkyCity24Payment)
class SkyCity24PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'account',
        'amount',
        'confirmed',
        'save_dt'
    )
    search_fields = ('order_id', 'account', 'client_name')


@admin.register(SkyPrivatbankPayment)
class SkyPrivatbankPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'contract_num',
        'amount',
        'save_dt'
    )
    search_fields = ('contract_num', 'client_name')
    date_hierarchy = 'save_dt'
    list_per_page = 200
