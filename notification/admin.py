from django.contrib import admin
from .models import Notification
class NotificationAdmin(admin.ModelAdmin):
    list_display=['notification_id','user','notification_type','booking', 'is_read']
    list_display_links = ['notification_id','user','notification_type','booking', 'is_read']

    def notification_id(self, obj):
        return obj.id

    notification_id.short_description = 'Notification ID'

admin.site.register(Notification, NotificationAdmin)
