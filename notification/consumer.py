# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connecting to artist')
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            print('groupname',self.group_name)
        else:
            print(self.user)
            print('not authenticated')
            self.group_name = None

        if self.group_name:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the artist from the group when they disconnect
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Handle incoming booking-related notifications dynamically
    async def booking_notification(self, event):
        booking_data = event['booking']
        booking_type = event.get('booking_type', 'new_booking')  # Default to 'new_booking'

        # Build the dynamic message based on notification_type
        if booking_type == 'new_booking':
            message = 'You have a new booking!'
        elif booking_type == 'cancelled_boooking':
            message = 'A booking has been cancelled.'
        elif booking_type == 'accepted_booking':
            message = 'Your booking has been accepted.'
        elif booking_type == 'paid_downpayment':
            message = 'We just received a downpayment for your booking.'
        else:
            message = 'You have a new notification.'

        # Send the dynamic message and booking data to the artist via WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'booking': booking_data,
            'booking_type': booking_type # Include this in case the frontend needs it
        }))
