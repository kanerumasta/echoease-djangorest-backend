# import json
from asgiref.sync import sync_to_async
# from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from channels.db import database_sync_to_async

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name
#         self.conversation = get_object_or_404(Conversation, code=self.room_name)
        

#         self.user = self.scope['user']
#         if self.user:
#             async_to_sync(self.channel_layer.group_add)(
#                 self.room_group_name, self.channel_name
#             )
#             self.accept()
#             print('Connected - ',self.user)
#         else:
#             self.disconnect()
#             print('User not valid')

      
#         self.accept()
#         print('Connected - ')

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )
#         print('Disconnected...')

#     def receive(self, text_data):

       
#         try:
#             message = Message.objects.create(conversation = self.conversation, author=self.user, content=text_data)
#             print('Saved message', message)
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name, {
#                     "type": "chat_message",
#                     "message": text_data,
#                     "author":self.user.email,
#                     "id":str(message.id),
#                     "date":str(message.date),
#                     "time":str(message.time)

#                 }
#         )
#         except Exception as e:
#             print(e)


#     def chat_message(self, event):
        
#         text_data = json.dumps(event)
        

#         self.send(text_data=text_data)


import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.conversation = await self.get_conversation_or_404(self.room_name)

        # if self.scope["user"] == AnonymousUser():
        #     return
        print(self.conversation)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print(text_data)
        # text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        message = text_data

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))


    
    @sync_to_async
    def get_conversation_or_404(self, room_name):
        return get_object_or_404(Conversation, code=room_name)