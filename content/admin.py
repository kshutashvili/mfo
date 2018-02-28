from django.contrib import admin

from content.models import Spoiler, StaticPage


@admin.register(Spoiler)
class SpoilerAdmin(admin.ModelAdmin):
    list_display = ('topic',)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'link')

