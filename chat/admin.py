from django.contrib import admin
from .models import Conversation, Message

class CustomAdminModel (admin.ModelAdmin):
    list_display = ['pk','created_at']
    list_display_links = ['pk','created_at']
    ordering = ['created_at']


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('pk','get_participants')

    def get_participants(self, obj):
        return ' AND '.join([participant.email for participant in obj.participants.all()])

    get_participants.short_description = "Participants"


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, CustomAdminModel)
