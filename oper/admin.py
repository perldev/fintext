from django.contrib import admin
from .models import (
    chat
)  


class chatAdmin(admin.ModelAdmin):
    list_display = ["uuid"]

admin.site.register(chat, chatAdmin)