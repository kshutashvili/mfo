from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext, gettext_lazy as _

from users.two_factor import OTPAdminSite
from users.models import (
    Profile, RequestPersonalArea, User,
    Questionnaire, RegistrationCountry
)


# Add 2FA authentication to the admin site
# admin.site.__class__ = OTPAdminSite


class ProfileInline(admin.StackedInline):
    model = Profile
    exclude = ('verify_code', 'two_authy')


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    list_display = (
        "mobile_phone",
        "email",
        "turnes_person_id",
        "is_superuser"
    )
    search_fields = ("turnes_person_id", )
    ordering = ('mobile_phone', )
    exclude = ('date_joined', )
    fieldsets = (
        (None, {'fields': ('mobile_phone', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', )}),
        (_('Important fields'), {'fields': ('turnes_person_id',
                                            'changed_default_password',
                                            'ready_for_turnes')}),
    )


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
