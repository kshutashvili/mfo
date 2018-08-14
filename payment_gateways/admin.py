from django.contrib import admin

from .models import *


@admin.register(EasypayPayment)
class EasypayPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'service_id',
        'order_id',
        'account',
        'confirmed'
    )


@admin.register(City24Payment)
class City24PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(PrivatbankPayment)
class PrivatbankPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'inrazpredelenie_id',
        'amount',
        'save_dt'
    )
