from django.contrib import admin
from .models import CashPointLocation, Orders, CurrencyProvider, Currency


class CashPointLocationAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]

admin.site.register(CashPointLocation, CashPointLocationAdmin)


class OrdersAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "expire_date"]

admin.site.register(Orders, OrdersAdmin)


class CurrencyProviderAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]

admin.site.register(CurrencyProvider, CurrencyProviderAdmin)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]

admin.site.register(Currency, CurrencyAdmin)
