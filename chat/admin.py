from django.contrib import admin
from .models import Conversation, Message

class CustomAdminModel (admin.ModelAdmin):
    list_display = ['pk', '__str__','date','time']
    list_display_links = ['pk', '__str__','date','time']
    ordering = ['date','time']


admin.site.register(Conversation, admin.ModelAdmin)
admin.site.register(Message, CustomAdminModel)