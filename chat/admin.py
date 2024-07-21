from django.contrib import admin
from .models import Conversation, Message

class CustomAdminModel (admin.ModelAdmin):
    list_display = ['pk', '__str__']


admin.site.register([Conversation, Message], CustomAdminModel)