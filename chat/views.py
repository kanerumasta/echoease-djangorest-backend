from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from .models import Conversation, Message
from django.shortcuts import get_object_or_404
from artists.models import Artist
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
import time
from .serializers import (
    ConversationSerializer
)
from rest_framework.response import Response
from users.models import UserAccount

class ConversationsView(APIView):
    def get(self, request):
        conversations = Conversation.objects.filter(participants = request.user).exclude(messages__isnull=True).exclude(deleted_for = request.user).exclude(blocked_users__isnull=False)
        serializer = ConversationSerializer(conversations, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConversationDetailView(APIView):
    def get(self, request, code):
        conversation = get_object_or_404(Conversation, code=code)
        serializer = ConversationSerializer(conversation, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, code):
        conversation = get_object_or_404(Conversation, code=code)

        messages  = conversation.messages
        for message in messages.all():
            message.mark_deleted = True
            message.save()
            print('deleted')

        conversation.deleted_for.add(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationView(APIView):
    def get(self, request, code=None, slug=None):
        current_user = request.user
        # Step 1: Get or create the conversation
        if code:
            # Retrieve conversation by code
            conversation = get_object_or_404(Conversation, code=code)
        elif slug:
            # Handle conversation with artist using slug
            artist = get_object_or_404(Artist, slug=slug)

            # Check if conversation already exists with both participants
            conversation = Conversation.objects.filter(participants=current_user).filter(participants=artist.user).first()

            if conversation is not None:
                conversation.deleted_for.clear()

            # If no conversation exists, create a new one
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(current_user, artist.user)  # Ensure participants are added here

        # Step 2: Retrieve messages for the conversation
        messages = conversation.messages.filter(mark_deleted=False).order_by('-created_at')  # Order by latest

        #Set messages as is_read
        messages.update(is_read=True)


        # Step 3: Paginate messages (show 15 messages per page)
        paginator = Paginator(messages, 15)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Step 4: Prepare the response data
        response_data = {
            'code': str(conversation.code),
            'messages': [{
                'id': message.id,
                'content': message.content,
                'author': message.author.email,
                'created_at': message.created_at,
                'is_read':message.is_read
            } for message in reversed(page_obj)],
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        }


        return JsonResponse(response_data)


class BlockUserView(APIView):
    def post(self, request, conversation_code, user_id):

        if not conversation_code or not user_id:
            return Response({"message": "Code and User Id is required"}, status=status.HTTP_400_BAD_REQUEST)

        conversation = get_object_or_404(Conversation, code=conversation_code)
        user_to_block = get_object_or_404(UserAccount, id=user_id)

        # Check if the user is already blocked
        if user_to_block in conversation.blocked_users.all():
            return Response({"message": "User is already blocked."}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the blocked_users list
        conversation.blocked_users.add(user_to_block)
        return Response({"message": "User blocked successfully."}, status=status.HTTP_200_OK)

    def get(self, request):
        blocked_conversations = Conversation.objects.filter(participants=request.user,blocked_users__isnull=False).distinct()
        serializer = ConversationSerializer(blocked_conversations,context={'request':request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UnblockUserView(APIView):
    def post(self, request):
        conversation_code = request.data.get('conversation_code')
        user_id = request.data.get('user_id')
        conversation = get_object_or_404(Conversation, code=conversation_code)
        user_to_unblock = get_object_or_404(UserAccount, id=user_id)
        # Remove the user from the blocked_users list
        conversation.blocked_users.remove(user_to_unblock)
        return Response({"message": "User unblocked successfully."}, status=status.HTTP_200_OK)

@api_view(['GET'])  # Fetch all unread messages count
def get_unread_messages_count(request):
    current_user = request.user

    # Get all conversations the current user is a part of
    user_conversations = Conversation.objects.filter(participants=current_user)

    # Count unread messages in those conversations
    unread_messages_count = Message.objects.filter(
        conversation__in=user_conversations,  # Use the relationship to filter by conversation
        is_read=False
    ).exclude(author=current_user).count()
    return Response({'unread_messages_count': unread_messages_count}, status=status.HTTP_200_OK)


@api_view(['POST'])
def set_conversation_read(request, code):
    conversation = get_object_or_404(Conversation, code=code)
    messages = conversation.messages.update(is_read=True)
    return Response(status=status.HTTP_204_NO_CONTENT)
