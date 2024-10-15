from rest_framework import serializers
from .models import Conversation, Message
from django.conf import settings
from users.serializers import UserAccountSerializer

User = settings.AUTH_USER_MODEL

class MessageSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id','author','content','created_at']

    def get_author(self, obj):
        return obj.author.email if obj.author else None

from rest_framework import serializers
from .models import Conversation

class ConversationSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['code', 'user', 'partner']

    def get_user(self, obj):
        # Get the current user from the request context
        current_user = self.context['request'].user
        return UserAccountSerializer(current_user).data

    def get_partner(self, obj):
        # Find the other participant in the conversation
        current_user = self.context['request'].user
        partner = obj.participants.exclude(id=current_user.id).first()  # Exclude the current user
        if partner:
            return UserAccountSerializer(partner).data
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "code": data['code'],
            "user": data['user'],
            "partner": data['partner']
        }

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     request = self.context.get('request')

    #     # Assuming you have access to the current user from the request
    #     current_user = request.user

    #     # Filter out the current user from the participants to find the partner
    #     partner = None
    #     participants = rep.get('participants', [])
    #     if len(participants) > 1:
    #         partner = next((p for p in participants if p['email'] != current_user.email), None)

    #     rep['partner'] = partner
    #     return rep

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
