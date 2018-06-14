from django.contrib import admin

from .models import *

# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'last_name', 'first_name', 'inn', 'resident'
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    def get_customer_last_name(self, obj):
        return obj.customer.last_name

    def get_customer_first_name(self, obj):
        return obj.customer.first_name

    list_display = (
        'id', 'type', 'get_customer_last_name',
        'get_customer_first_name'
    )
    get_customer_last_name.short_description = "Фамилия"
    get_customer_first_name.short_description = "Имя"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    def get_customer_last_name(self, obj):
        return obj.customer.last_name

    def get_customer_first_name(self, obj):
        return obj.customer.first_name

    list_display = (
        'id', 'country', 'type', 'get_customer_last_name',
        'get_customer_first_name'
    )


@admin.register(ScanDocument)
class ScanDocumentAdmin(admin.ModelAdmin):
    def get_customer_last_name(self, obj):
        return obj.customer.last_name

    def get_customer_first_name(self, obj):
        return obj.customer.first_name

    list_display = (
        'id', 'extension', 'type', 'get_customer_last_name',
        'get_customer_first_name'
    )