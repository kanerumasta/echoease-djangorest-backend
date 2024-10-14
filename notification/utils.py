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

def notify_user_of_cancelled_booking(user, booking):
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
