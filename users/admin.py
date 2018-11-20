from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from users.two_factor import OTPAdminSite
from users.models import (
    Profile, RequestPersonalArea, User,
    Questionnaire, RegistrationCountry
)


# Add 2FA authentication to the admin site
admin.site.__class__ = OTPAdminSite


class ProfileInline(admin.StackedInline):
    model = Profile
    exclude = ('verify_code', 'two_authy')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "mobile_phone",
        "email",
        "turnes_person_id",
        "is_superuser"
    )
    search_fields = ("turnes_person_id", )


@admin.register(RequestPersonalArea)
class RequestPersonalAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract_num', 'mobile_phone_number')
    search_fields = ('name', 'mobile_phone_number')
    list_filter = ('contract_num', )


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'mobile_phone', 'email', 'itn')


@admin.register(RegistrationCountry)
class RegistrationCountryAdmin(admin.ModelAdmin):
    pass
