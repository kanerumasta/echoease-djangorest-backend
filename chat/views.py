from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views  import APIView
from .serializers import MessageSerializer, ConversationSerializer,CreateConversationSerializer, ConversationMessagesSerializer
from .models import Conversation
from rest_framework.response import Response
from django.db.models import Count, Q


class ConversationView(APIView):
    def get(self,request,code = None):
        if code:
            conversation = Conversation.objects.get(code = code)
            serializer = ConversationMessagesSerializer(conversation)
            return Response(serializer.data, status = status.HTTP_200_OK)
    
        conversations = Conversation.objects.filter(users=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self,request):
        try:
            data = request.data
            serializer = CreateConversationSerializer(data = data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                # conversation = Conversation.objects.annotate(num_users = Count('users')).filter(num_users=2,users = request.user).filter(users = serializer.validated_data['receiver']).distinct()
                # if conversation.exists():
                #     conversation = conversation.first()
                #     serializer = ConversationSerializer(conversation)
                #     return Response(serializer.data, status = status.HTTP_200_OK)
                # conversation = Conversation.objects.create()
                # conversation.users.set([request.user, serializer.validated_data.get('receiver')])
                # conversation.save()
                # serializer = ConversationSerializer(conversation)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'detail':'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessagesView(APIView):
    def get(self,request, code):
        conversation = get_object_or_404(Conversation, code = code)
        message_serializer = MessageSerializer(conversation.messages, many=True)
        return Response(message_serializer.data, status = status.HTTP_200_OK)


    def post(self, request):
        serializer = MessageSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


    