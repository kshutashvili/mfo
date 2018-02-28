from django.contrib import admin

from communication.models import Contact, PhoneNumber, Agreement, Email


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email',)

