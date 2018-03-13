from django.contrib import admin

from vacancy import models


@admin.register(models.Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    exclude = ('name', 'demands', 'conditions')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    exclude = ('name',)

