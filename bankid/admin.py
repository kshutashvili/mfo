from django.contrib import admin
from django import forms

from .models import *
from .widgets import AdminFileWidget

# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'last_name', 'first_name', 'inn', 'resident',
        'created_dt'
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    def get_customer_last_name(self, obj):
        return obj.customer.last_name

    def get_customer_first_name(self, obj):
        return obj.customer.first_name

    list_display = (
        'id', 'type', 'get_customer_last_name',
        'get_customer_first_name', 'created_dt'
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
        'get_customer_first_name', 'created_dt'
    )


class SecureFileAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SecureFileAdminForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget = AdminFileWidget()

    class Meta:
        model = ScanDocument
        fields = '__all__'


@admin.register(ScanDocument)
class ScanDocumentAdmin(admin.ModelAdmin):
    def get_customer_last_name(self, obj):
        return obj.customer.last_name

    def get_customer_first_name(self, obj):
        return obj.customer.first_name

    list_display = (
        'id', 'extension', 'type', 'get_customer_last_name',
        'get_customer_first_name', 'created_dt'
    )
    form = SecureFileAdminForm


@admin.register(BankIDLog)
class BankIDLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'created_dt')
    search_fields = ('type', 'message')
    list_filter = ('type', )
