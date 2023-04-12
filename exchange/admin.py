from django.contrib import admin
from .models import CashPointLocation


class CashPointLocationAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]

admin.site.register(CashPointLocation, CashPointLocationAdmin)
