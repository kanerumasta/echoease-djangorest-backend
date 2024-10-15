from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from .models import Conversation, Message
from django.shortcuts import get_object_or_404
from artists.models import Artist
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import status
from .serializers import (
    ConversationSerializer
)
from rest_framework.response import Response

class ConversationsView(APIView):
    def get(self, request):
        conversations = Conversation.objects.filter(participants = request.user)
        serializer = ConversationSerializer(conversations, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class ConversationView(APIView):
    def get(self, request, code=None, slug=None):
        print('USER', request.user)
        current_user = request.user

        # Step 1: Get or create the conversation
        if code:
            # Retrieve conversation by code
            conversation = get_object_or_404(Conversation, code=code)
        elif slug:
            # Handle conversation with artist using slug
            artist = get_object_or_404(Artist, slug=slug)

            # Check if conversation already exists with both participants
            conversation = Conversation.objects.filter(
                Q(participants=current_user) & Q(participants=artist.user)
            ).first()

            # If no conversation exists, create a new one
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(current_user, artist.user)

            # Step 2: Retrieve messages for the conversation
        messages = conversation.messages.all().order_by('-created_at') # Order by latest

        # messages = messages.reverse()
        # Step 3: Paginate messages (show 15 messages per page)
        paginator = Paginator(messages, 8)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Step 4: Prepare the response data
        response_data = {
            'code': str(conversation.code),
            'messages': [{
                'id': message.id,
                'content': message.content,
                'author': message.author.email,
                'created_at': message.created_at
            } for message in reversed(page_obj)],
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        }

        return JsonResponse(response_data)

# from django.shortcuts import get_object_or_404
# from rest_framework import status
# from rest_framework.views  import APIView
# from .serializers import MessageSerializer, ConversationSerializer,CreateConversationSerializer, ConversationMessagesSerializer
# from .models import Conversation
# from users.models import UserAccount
# from artists.models import Artist
# from rest_framework.response import Response
# from django.db.models import Count, Q


# def get_conversation_by_code(request,code):
#     conversation = get_object_or_404(Conversation, code=code)




# # class ConversationView(APIView):
# #     def get(self,request,code = None, slug=None):
# #         user = request.user
# #         if code:
# #             conversation = Conversation.objects.get(code = code)
# #             serializer = ConversationSerializer(conversation,context={'request':request})
# #             return Response(serializer.data, status = status.HTTP_200_OK)

# #         if slug:
# #             # Handling conversations with an artist
# #             artist = get_object_or_404(Artist, slug=slug)


# #             # Check if conversation already exists with the artist
# #             conversation = Conversation.objects.filter(participants=artist.user).filter( participants=user).first()

# #             if not conversation:
# #                 # Create a new conversation
# #                 conversation = Conversation.objects.create()
# #                 conversation.participants.add(user)
# #                 conversation.participants.add(artist.user)
# #                 conversation.save()
# #             serializer = ConversationSerializer(conversation,context={'request':request})
# #             return Response(serializer.data, status= status.HTTP_200_OK)
# #         conversations = Conversation.objects.filter(participants=request.user)
# #         serializer = ConversationSerializer(conversations, many=True,context={'request':request})
# #         return Response(serializer.data, status=status.HTTP_200_OK)


# #     def post(self,request):
# #         user = request.user


# #         # Handling conversations with another user
# #         receiver_id = request.data.get('receiver')

# #         if not receiver_id:
# #             return Response({'message': 'Receiver ID is required'}, status=status.HTTP_400_BAD_REQUEST)

# #         receiver_id = int(receiver_id)

# #         if user.id == receiver_id:
# #             return Response({'message': 'You can\'t create a conversation with yourself'}, status=status.HTTP_400_BAD_REQUEST)

# #         receiver = get_object_or_404(UserAccount, id=receiver_id)

# #         # Check if conversation already exists with the receiver
# #         conversation = Conversation.objects.filter(participants=receiver).filter(participants = user).first()

# #         if not conversation:
# #             # Create a new conversation
# #             conversation = Conversation.objects.create()
# #             conversation.participants.add(user, receiver)
# #             conversation.save()

# #         # Serialize and return the conversation
# #         serializer = ConversationSerializer(conversation)
# #         return Response(serializer.data, status=status.HTTP_200_OK)


# # class MessagesView(APIView):
# #     def get(self,request, code):
# #         conversation = get_object_or_404(Conversation, code = code)
# #         message_serializer = MessageSerializer(conversation.messages, many=True) # type: ignore
# #         return Response(message_serializer.data, status = status.HTTP_200_OK)


# #     def post(self, request):
# #         serializer = MessageSerializer(data = request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# # def get_my_conversations(request):
# #     user = request.user
# #     conversations = user.conversations.all()
# #     serializer = ConversationSerializer(conversations, many=True)
# #     return Response(serializer.data, status = status.HTTP_200_OK)
