from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from users.models import Profile, RequestPersonalArea, User


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
