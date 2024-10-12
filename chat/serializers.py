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

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        # Assuming you have access to the current user from the request
        current_user = request.user

        # Filter out the current user from the participants to find the partner
        partner = None
        participants = rep.get('participants', [])
        if len(participants) > 1:
            partner = next((p for p in participants if p['email'] != current_user.email), None)

        rep['partner'] = partner
        return rep

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
