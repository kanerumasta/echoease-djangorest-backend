from rest_framework import serializers
from .models import Conversation, Message
from django.conf import settings
from users.serializers import UserAccountSerializer

User = settings.AUTH_USER_MODEL

class MessageSerializer(serializers.ModelSerializer):
    
    author = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id','author','content', 'date','time']

    def get_author(self, obj):
        return obj.author.email if obj.author else None



class ConversationSerializer(serializers.ModelSerializer):
    participants = UserAccountSerializer(read_only=True, many=True)
    class Meta:
        model = Conversation
        fields = ['code', 'participants']


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
    
    


        

