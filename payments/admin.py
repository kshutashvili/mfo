from solo.admin import SingletonModelAdmin

from django.contrib import admin

from .models import Payment, KeyFor4billAPI, PaymentPrivat


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'service_id', 'amount', 'status', 'is_paid')


@admin.register(KeyFor4billAPI)
class KeyFor4billAPIAdmin(SingletonModelAdmin):
    pass


@admin.register(PaymentPrivat)
class PaymentPrivatAdmin(admin.ModelAdmin):
    list_display = ('tpp_id', 'contract_num', 'amount', 'created_dt')
