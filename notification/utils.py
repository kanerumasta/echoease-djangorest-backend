from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_artist_of_new_booking(artist, booking):
    channel_layer = get_channel_layer()
    group_name = f"user_{artist.id}"
    print('GROUP NAME IS',group_name)

    # Send message to artist's WebSocket group
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'booking_notification',  # This should match the function name in ArtistConsumer
            'booking': {
                'id': booking.id,
                'client': f'{booking.client.first_name} {booking.client.last_name}',
                'event_date': str(booking.event_date)
            },
            'booking_type':'new_booking'
        }
    )



def notify_client_of_accepted_booking(client, booking):
    channel_layer = get_channel_layer()
    group_name = f"user_{client.id}"

    # Send message to artist's WebSocket group
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'booking_notification',  # This should match the function name in ArtistConsumer
            'booking': {
                'id': booking.id,
                'artist': f'{booking.artist.user.first_name} {booking.artist.user.last_name}',
                'event_date': str(booking.event_date)
            },
            'booking_type':'accepted_booking'
        }
    )


def notify_artist_of_paid_downpayment(artist, booking): # new upcoming event
    channel_layer = get_channel_layer()
    group_name = f"user_{artist.id}"

    # Send message to artist's WebSocket group
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'booking_notification',  # This should match the function name in ArtistConsumer
            'booking': {
                'id': booking.id,
                'client': f'{booking.client.first_name} {booking.client.last_name}',
                'event_date': str(booking.event_date)
            },
            'booking_type':'paid_downpayment'
        }
    )
def notify_artist_of_paid_final_payment(artist, booking): # new upcoming event
    channel_layer = get_channel_layer()
    group_name = f"user_{artist.id}"

    # Send message to artist's WebSocket group
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'booking_notification',  # This should match the function name in ArtistConsumer
            'booking': {
                'id': booking.id,
                'client': f'{booking.client.first_name} {booking.client.last_name}',
                'event_date': str(booking.event_date)
            },
            'booking_type':'payout'
        }
    )

def notify_client_of_cancelled_booking(user, booking):
    channel_layer = get_channel_layer()
    group_name = f"user_{user.id}"
    # Send message to artist's WebSocket group
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'booking_notification',  # This should match the function name in ArtistConsumer
            'booking': {
                'id': booking.id,
                'artist': f'{booking.artist.user.first_name} {booking.artist.user.last_name}',
                'event_date': str(booking.event_date)
            },
            'booking_type':'cancelled_booking'
        }
    )

def notify_client_of_rejected_booking(user,booking):
    channel_layer = get_channel_layer()
    group_name = f"user_{user.id}"

    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'booking_notification',
            'booking': {
                'id': booking.id,
                'artist': f'{booking.artist.user.first_name} {booking.artist.user.last_name}',
                'event_date': str(booking.event_date)
            },
            'booking_type':'rejected_booking'
        }
    )
def notify_user_of_new_message(receiver, sender):
    channel_layer = get_channel_layer()
    group_name = f"user_{receiver.id}"
    # Send message to receiver's WebSocket group
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type':'message_notification',
            'sender': f'{sender.first_name} {sender.last_name}',
        }
    )

def notify_application_accepted(user):
    channel_layer = get_channel_layer()
    group_name = f"user_{user.id}"

    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'application_notification',
            'application_type':'accepted',
            'message':'Your application has been accepted',
            'user': f'{user.first_name} {user.last_name}'
        }
    )

def notify_new_sent_request(receiver, sender): #receiver and sender are both UserAccount instance
    channel_layer = get_channel_layer()

    group_name = f"user_{receiver.user.id}"

    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'connection_notification',
            'message': f'{sender.first_name} {sender.last_name} sent you a connection request.'
        }
    )
def notify_accepted_request(receiver, sender): #receiver and sender are both UserAccount instance
    channel_layer = get_channel_layer()

    group_name = f"user_{receiver.user.id}"

    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'connection_notification',
            'message': f'{sender.user.first_name} {sender.user.last_name} accepted your connection request.'
        }
    )

def notify_refunded_payment(user):
    channel_layer = get_channel_layer()
    group_name = f"user_{user.id}"
    async_to_sync(channel_layer.group_send)( # type: ignore
        group_name,
        {
            'type': 'refund_notification',
            'message': f'Your payment has been refunded.'
        }
    )
