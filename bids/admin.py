from rangefilter.filter import DateRangeFilter

from django.contrib import admin

from .models import Bid


class WmIDListFilter(admin.SimpleListFilter):

    title = 'Указан wm ID'

    parameter_name = 'wm_id__exact'

    def lookups(self, request, model_admin):

        return (
            ('empty', 'Пустое'),
            ('filled', 'Указано'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'empty':
            return queryset.filter(wm_id__exact='')

        if self.value() == 'filled':
            return queryset.exclude(wm_id__exact='')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = (
        'contact_phone',
        'city',
        'wm_id',
        'any_param',
        'created_dt',
        'updated_dt'
    )
    list_filter = (
        ('created_dt', DateRangeFilter),
        WmIDListFilter
    )
