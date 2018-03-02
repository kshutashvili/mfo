from django.contrib import admin

from content import models


@admin.register(models.Spoiler)
class SpoilerAdmin(admin.ModelAdmin):
    list_display = ('topic',)


@admin.register(models.StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'link')


@admin.register(models.MenuAboutItem)
class MenuAboutItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')


@admin.register(models.MenuFooterItem)
class MenuFooterItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')


@admin.register(models.MenuFooterBlock)
class MenuFooterBlockAdmin(admin.ModelAdmin):
    list_display = ('order', 'name')

