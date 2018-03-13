from django.contrib import admin

from content import models


@admin.register(models.Spoiler)
class SpoilerAdmin(admin.ModelAdmin):
    list_display = ('topic',)
    exclude = ('topic', 'content_left', 'content_right')


@admin.register(models.StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'link')
    exclude = ('title',)


@admin.register(models.MenuAboutItem)
class MenuAboutItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    exclude = ('name',)


@admin.register(models.MenuFooterItem)
class MenuFooterItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')
    exclude = ('name',)


@admin.register(models.MenuFooterBlock)
class MenuFooterBlockAdmin(admin.ModelAdmin):
    list_display = ('order', 'name')
    exclude = ('name',)


@admin.register(models.MenuHeaderItem)
class MenuHeaderItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'link')
    exclude = ('name',)


@admin.register(models.MenuHeaderBlock)
class MenuHeaderBlockAdmin(admin.ModelAdmin):
    list_display = ('__str__', )


@admin.register(models.JobStaticPage)
class JobStaticPageAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('text',)


@admin.register(models.GetCredit)
class GetCreditAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = ('title', 'text')


@admin.register(models.CreditRateStatic)
class CreditRateStaticAdmin(admin.ModelAdmin):
    list_display = ('title', 'text')
    exclude = ('title', 'text')


@admin.register(models.Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('text',)


@admin.register(models.AdvantageStatic)
class AdvantageStaticAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = ('title', 'text')


@admin.register(models.CloseCredit)
class CloseCreditAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = ('title', 'text')


@admin.register(models.CloseCreditStatic)
class CloseCreditStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('title',)


@admin.register(models.SecurityItem)
class SecutiryItemAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('text',)


@admin.register(models.SecurityStatic)
class SecurityStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.DiscountStatic)
class DiscountStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('title', 'text')


@admin.register(models.ImportantAspect)
class ImportantAspectAdmin(admin.ModelAdmin):
    list_display = ('title', 'text',)
    exclude = ('title', 'text')


@admin.register(models.AboutUsStatic)
class AboutUsStaticAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'link', )
    exclude = ('title_top', 'meta_title', 'meta_description', 'title', 'subtitle', 
               'text', 'middle_title', 'middle_text', 'important_title')


@admin.register(models.MainPageTopBlockStatic)
class MainPageTopBlockStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'footer')


@admin.register(models.MainPageStatic)
class MainPageStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('title', 'meta_title', 'meta_description',)


@admin.register(models.IndexPageStatic)
class IndexPageStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.CreditInformation)
class CreditInformationAdmin(admin.ModelAdmin):
    list_display = ('title',)
    exclude = ('title', 'text')


@admin.register(models.CreditInformationBlockStatic)
class CreditInformationBlockStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    exclude = ('text',)

