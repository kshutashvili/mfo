from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import User
from users.models import Profile, RequestPersonalArea


class ProfileInline(admin.StackedInline):
    model = Profile
    exclude = ('verify_code', 'two_authy')


class UserAdmin(auth_admin.UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(RequestPersonalArea)
class RequestPersonalAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract_num', 'mobile_phone_number')
    search_fields = ('name', 'mobile_phone_number')
    list_filter = ('contract_num', )
