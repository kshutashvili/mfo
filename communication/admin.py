from solo.admin import SingletonModelAdmin

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


@admin.register(models.Resume)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone', 'email', 'city')


@admin.register(models.SuccessFormStatic)
class SuccessFormStaticAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = ('title', 'text', 'extra_text')


@admin.register(models.UserExistMessage)
class UserExistMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'updated_at', 'created_at', 'is_closed')
    list_display_links = ('content', 'updated_at', 'created_at')
    list_editable = ('is_closed',)
    exclude = ('end_message', 'is_read')


@admin.register(models.QuestionComment)
class QuestionCommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at', 'is_admin')
    list_display_links = ('content', 'created_at')
    list_editable = ('is_admin',)


@admin.register(models.QuestionConfig)
class QuestionConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'message')
    list_display_links = None
    list_editable = ('message', 'name')
    exclude = ('name', 'message')


@admin.register(models.CallbackSuccessForm)
class CallbackSuccessFormAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.CallbackFailForm)
class CallbackFailFormAdmin(SingletonModelAdmin):
    list_display = ('__str__',)


@admin.register(models.SocialNetUnderHeader)
class SocialNetUnderHeaderFormAdmin(admin.ModelAdmin):
    list_display = ('link',)
