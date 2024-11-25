from rest_framework import serializers
from .models import Conversation, Message
from django.conf import settings
from users.serializers import UserAccountSerializer
from django.utils import timezone
from datetime import datetime

User = settings.AUTH_USER_MODEL

class MessageSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id','author','content','created_at','is_read']

    def get_author(self, obj):
        return obj.author.email if obj.author else None

from rest_framework import serializers
from .models import Conversation

class ConversationSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    unread_messages_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['code', 'user', 'partner','unread_messages_count','last_message', 'last_message_time']

    def get_last_message(self, obj):
        return obj.last_message


    def get_last_message_time(self, obj):
        return obj.last_message_time

    def get_user(self, obj):
        # Get the current user from the request context
        current_user = self.context['request'].user
        return UserAccountSerializer(current_user,context={'request':self.context.get('request',None)}).data

    def get_partner(self, obj):
        # Find the other participant in the conversation
        current_user = self.context['request'].user
        partner = obj.participants.exclude(id=current_user.id).first()  # Exclude the current user
        if partner:
            return UserAccountSerializer(partner,context=self.context).data
        return None
    def get_unread_messages_count(self, obj):
        current_user = self.context['request'].user
        unread_messages = obj.messages.filter(is_read=False).exclude(author=current_user)
        print(f"Unread messages for {current_user.email}: {unread_messages.count()}")  # Log count
        return unread_messages.count()
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "code": data['code'],
            "user": data['user'],
            "partner": data['partner'],
            "unread_messages_count": data['unread_messages_count'],
            "last_message": data['last_message'],
            "last_message_time": data['last_message_time'],
        }


class ConversationMessagesSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ['messages']

class CreateConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['users']

# class CreateConversationSerializer(serializers.Serializer):
#     email = serializers.EmailField()
