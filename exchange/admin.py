from django.contrib import admin
from .models import (
    CashPointLocation, 
    Orders, 
    CurrencyProvider, 
    Currency, 
    Invoice,
    PoolAccounts,
    FiatAccounts,
    Trans
)  


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


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "currency"]

admin.site.register(Invoice, InvoiceAdmin)


class PoolAccountsAdmin(admin.ModelAdmin):
    list_display = ["currency", "address", "pub_date"]

admin.site.register(PoolAccounts, PoolAccountsAdmin)


class FiatAccountsAdmin(admin.ModelAdmin):
    list_display = ["id", "card_number"]

admin.site.register(FiatAccounts, FiatAccountsAdmin)


class TransAdmin(admin.ModelAdmin):
    list_display = ["id", "currency", "amnt", "status"]

admin.site.register(Trans, TransAdmin)
