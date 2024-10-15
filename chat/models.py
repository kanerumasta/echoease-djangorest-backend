from django.db import models
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    deleted_for = models.ManyToManyField(User, related_name='deleted_conversations', blank=True)

    def __str__(self):
        return str(self.code)




class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE,null=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    create_at = models.DateTimeField(auto_now_add=True)
