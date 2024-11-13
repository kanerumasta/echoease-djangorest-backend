# import json
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .serializers import MessageSerializer
from notification.utils import notify_user_of_new_message
from channels.layers import get_channel_layer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('attempt to connect')
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.conversation = await self.get_conversation_or_404(self.room_name)
        if self.scope['user'] == AnonymousUser():
            print('anon')
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


#PUT AUTHOR TO CONVERSATION
    async def receive(self, text_data):
        message = text_data
        print(message)

        if self.scope['user']:
            new_message = await sync_to_async(Message.objects.create)(
                conversation = self.conversation,
                author = self.scope['user'],
                content = message
            )
            serializer = MessageSerializer(new_message)


             # Send message notification
            receiver = await self.get_receiver()  # Use async method to fetch receiver
            if receiver:
                notif_channel_layer = get_channel_layer()
                group_name = f"user_{receiver.id}"
                sender = self.scope['user']
                # Send message to receiver's WebSocket group
                await notif_channel_layer.group_send(  # type: ignore
                    group_name,
                    {
                        'message':message,
                        'type': 'message_notification',
                        'sender': f'{sender.first_name} {sender.last_name}',
                    }
                )




        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message":serializer.data}
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps( message))



    @sync_to_async
    def get_conversation_or_404(self, room_name):
        return get_object_or_404(Conversation, code=room_name)
    @sync_to_async
    def get_receiver(self):
        # Fetch the first participant who is not the sender (scope['user'])
        return self.conversation.participants.exclude(id=self.scope['user'].id).first()
