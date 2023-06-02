from django.contrib import admin
from .models import ExchangePage, StaticPage, PageText


class ExchangePageAdmin(admin.ModelAdmin):
    list_display = ["id", "title_ru"]

admin.site.register(ExchangePage, ExchangePageAdmin)


class StaticPageAdmin(admin.ModelAdmin):
    list_display = ["id", "title_ru"]

admin.site.register(StaticPage, StaticPageAdmin)



class PageTextAdmin(admin.ModelAdmin):
    list_display = ["id", "title_ru"]

admin.site.register(PageText, PageTextAdmin)



