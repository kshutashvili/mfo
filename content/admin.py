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


@admin.register(models.JobStaticPage)
class JobStaticPageAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.GetCredit)
class JobStaticPageAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.CreditRateStatic)
class CreditRateStaticAdmin(admin.ModelAdmin):
    list_display = ('title', 'text')


@admin.register(models.Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.AdvantageStatic)
class AdvantageStaticAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.CloseCredit)
class CloseCreditAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.CloseCreditStatic)
class CloseCreditStaticAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.SecurityItem)
class SecutiryItemAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.SecurityStatic)
class SecurityStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.DiscountStatic)
class DiscountStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.ImportantAspect)
class ImportantAspectAdmin(admin.ModelAdmin):
    list_display = ('title', 'text',)


@admin.register(models.AboutUsStatic)
class AboutUsStaticAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'link', )


@admin.register(models.MainPageTopBlockStatic)
class MainPageTopBlockStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'footer')


@admin.register(models.MainPageStatic)
class MainPageStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.IndexPageStatic)
class IndexPageStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(models.CreditInformation)
class CreditInformationAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.CreditInformationBlockStatic)
class CreditInformationBlockStaticAdmin(admin.ModelAdmin):
    list_display = ('__str__',)

