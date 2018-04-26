from solo.admin import SingletonModelAdmin

from django.contrib import admin

from .models import Payment, KeyFor4billAPI


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(KeyFor4billAPI)
class KeyFor4billAPIAdmin(SingletonModelAdmin):
    pass
