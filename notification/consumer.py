# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"

        else:
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

        # Define a dictionary to map booking types to professional messages
        booking_messages = {
            'new_booking': 'A new booking request has been received.',
            'cancelled_booking': 'The booking has been canceled by the client.',
            'accepted_booking': 'Your booking request has been confirmed.',
            'rejected_booking': 'The booking request has been declined.',
            'paid_downpayment': 'A down payment for your booking has been successfully received.',
            'payout': 'You received a payment for you booking.'
        }

        # Get the message from the dictionary, or use a default message for unknown booking types
        message = booking_messages.get(booking_type, 'You have a new notification related to your booking.')

        # Send the notification and booking data via WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'booking': booking_data,
            'booking_type': booking_type,
            'notification_type':'booking'
        }))

   # Handle incoming message-related notifications dynamically
    async def message_notification(self, event):
        sender = event['sender']
        message = event['message']

        # Send the message notification via WebSocket
        await self.send(text_data=json.dumps({
            'message': f'{sender}: {message}',
            'notification_type': 'message'
        }))

    async def application_notification(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'notification_type': 'application'
        }))

    async def connection_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'notification_type': 'connection'
        }))
    async def refund_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'notification_type': 'refund'
        }))
