from django.contrib import admin

from communication import models


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)


@admin.register(models.Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email',)


@admin.register(models.Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'text')

