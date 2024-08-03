from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views  import APIView
from .serializers import MessageSerializer, ConversationSerializer,CreateConversationSerializer, ConversationMessagesSerializer
from .models import Conversation
from users.models import UserAccount
from rest_framework.response import Response
from django.db.models import Count, Q


class ConversationView(APIView):
    def get(self,request,code = None):
        if code:
            conversation = Conversation.objects.get(code = code)
            serializer = ConversationMessagesSerializer(conversation)
            return Response(serializer.data, status = status.HTTP_200_OK)
    
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self,request):
        try:
            user = request.user
            receiver_id = request.data['receiver']
            if user.id == int(receiver_id):
                return Response({'message':'You can\'t create conversation with yourself'}, status= status.HTTP_400_BAD_REQUEST)
            receiver = get_object_or_404(UserAccount, id=int(receiver_id))
            if receiver:
                conversation = Conversation.objects.filter(participants=receiver).filter(participants = user).first()
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(user, receiver)
                conversation.save()
                
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error',e)
            return Response({'detail':'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


    