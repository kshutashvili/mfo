from django.contrib import admin
from .models import Bid


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
