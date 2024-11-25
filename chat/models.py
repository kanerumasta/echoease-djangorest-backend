from django.db import models
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    deleted_for = models.ManyToManyField(User, related_name='deleted_conversations', blank=True)
    blocked_users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return str(self.code)
    @property
    def last_message(self):
        last_msg = self.messages.order_by('-created_at').first()
        return last_msg.content if last_msg else ""
    @property
    def last_message_time(self):
        last_msg = self.messages.order_by('-created_at').first()
        if last_msg:
            return timezone.localtime(last_msg.created_at).strftime('%I:%M %p')  # 10:20 AM format
        return ""

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE,null=True)
    is_read = models.BooleanField(default=False)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    created_at = models.DateTimeField(auto_now_add=True)
    mark_deleted =  models.BooleanField(default=False)
