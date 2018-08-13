from django.contrib import admin

from .models import *


@admin.register(Tcredits)
class TcreditsAdmin(admin.ModelAdmin):
    pass


@admin.register(Tpersons)
class TpersonsAdmin(admin.ModelAdmin):
    pass


@admin.register(Tcash)
class TcashAdmin(admin.ModelAdmin):
    pass


@admin.register(EasypayPayment)
class EasypayPaymentAdmin(admin.ModelAdmin):
    pass


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
