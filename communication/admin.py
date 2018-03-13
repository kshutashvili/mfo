from django.contrib import admin

from communication import models


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('title', 'meta_title', 'meta_description', 'address',
               'schedule', 'title_text', 'footer_text')


@admin.register(models.PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)


@admin.register(models.Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('text',)


@admin.register(models.Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email',)


@admin.register(models.Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'text')


@admin.register(models.SocialNet)
class SocialNetAdmin(admin.ModelAdmin):
    list_display = ('link',)


@admin.register(models.BlogItem)
class BlogItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'date',)
    exclude = ('title', 'text')


@admin.register(models.LastArticles)
class LastArticlesAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.FaqCategory)
class FaqCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    exclude = ('name',)


@admin.register(models.FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    exclude = ('name',)


@admin.register(models.WriteUsEmail)
class WriteUsEmailAdmin(admin.ModelAdmin):
    list_display = ('email',)


@admin.register(models.HotLinePhone)
class HotLinePhoneAdmin(admin.ModelAdmin):
    list_display = ('number', 'schedule_start', 'schedule_end')


@admin.register(models.FaqPageStatic)
class FaqPageStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('title', 'meta_title', 'meta_description')


@admin.register(models.BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('name',)

