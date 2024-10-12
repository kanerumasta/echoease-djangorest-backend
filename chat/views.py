from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views  import APIView
from .serializers import MessageSerializer, ConversationSerializer,CreateConversationSerializer, ConversationMessagesSerializer
from .models import Conversation
from users.models import UserAccount
from artists.models import Artist
from rest_framework.response import Response
from django.db.models import Count, Q


class ConversationView(APIView):
    def get(self,request,code = None, slug=None):
        user = request.user
        if code:
            conversation = Conversation.objects.get(code = code)
            serializer = ConversationSerializer(conversation,context={'request':request})
            return Response(serializer.data, status = status.HTTP_200_OK)

        if slug:
            # Handling conversations with an artist
            artist = get_object_or_404(Artist, slug=slug)
            artist_user = get_object_or_404(UserAccount, pk=artist.user.pk)

            # Check if conversation already exists with the artist
            conversation = Conversation.objects.filter(participants=artist_user).filter( participants=user).first()

            if not conversation:
                # Create a new conversation
                conversation = Conversation.objects.create()
                conversation.participants.add(user, artist_user)
                conversation.save()
            serializer = ConversationSerializer(conversation,context={'request':request})
            return Response(serializer.data, status= status.HTTP_200_OK)
        print('here')
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self,request):
        user = request.user


        # Handling conversations with another user
        receiver_id = request.data.get('receiver')

        if not receiver_id:
            return Response({'message': 'Receiver ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        receiver_id = int(receiver_id)

        if user.id == receiver_id:
            return Response({'message': 'You can\'t create a conversation with yourself'}, status=status.HTTP_400_BAD_REQUEST)

        receiver = get_object_or_404(UserAccount, id=receiver_id)

        # Check if conversation already exists with the receiver
        conversation = Conversation.objects.filter(participants=receiver).filter(participants = user).first()

        if not conversation:
            # Create a new conversation
            conversation = Conversation.objects.create()
            conversation.participants.add(user, receiver)
            conversation.save()

        # Serialize and return the conversation
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessagesView(APIView):
    def get(self,request, code):
        conversation = get_object_or_404(Conversation, code = code)
        message_serializer = MessageSerializer(conversation.messages, many=True) # type: ignore
        return Response(message_serializer.data, status = status.HTTP_200_OK)


    def post(self, request):
        serializer = MessageSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
