# # import json
# from asgiref.sync import sync_to_async
# from django.shortcuts import get_object_or_404

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"
#         self.conversation = await self.get_conversation_or_404(self.room_name)
#         print(self.scope['user'])
#         if self.scope['user'] == AnonymousUser():
#             return
#         print(self.conversation)
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name) # type: ignore
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name) # type: ignore


# #PUT AUTHOR TO CONVERSATION
#     async def receive(self, text_data):
#         message = text_data

#         if self.scope['user']:
#             # new_message = await sync_to_async(Message.objects.create)(
#             #     conversation = self.conversation,
#             #     author = self.scope['user'],
#             #     content = message
#             # )
#             # serializer = MessageSerializer(new_message)
#             # print(serializer.data)


#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat_message", "message":serializer.data}
#         )

#     async def chat_message(self, event):
#         message = event["message"]

#         await self.send(text_data=json.dumps( message))


    
#     @sync_to_async
#     def get_conversation_or_404(self, room_name):
#         return get_object_or_404(Conversation, code=room_name)