from django.contrib import admin
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    pass
