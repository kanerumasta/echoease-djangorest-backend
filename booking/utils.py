
from booking.models import Booking
from notification.models import Notification


def create_new_booking_notification(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        notification_type = 'new_booking'
        title = 'New Booking Inquiry!'
        description = f'You have a new booking inquiry for an event on {booking.event_date} from {booking.client.first_name.capitalize()} {booking.client.last_name.capitalize()}' # type: ignore

        Notification.objects.create(
            user=booking.artist.user,
            notification_type=notification_type,
            title=title,
            description=description,
            booking=booking
        )
    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist.")


def create_booking_confirmation_notification(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        notification_type = 'booking_confirmation'
        title = 'Booking Confirmed!'
        description = f'Your booking for an event on {booking.event_date} with {booking.artist.user.first_name} {booking.artist.user.last_name} has been confirmed.'

        Notification.objects.create(
            user=booking.client,
            notification_type=notification_type,
            title=title,
            description=description,
            booking=booking
        )
    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist.")

def create_booking_rejected_notification(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        notification_type = 'booking_rejected'
        title = 'Booking Rejected!'
        description = f'Your booking for an event on {booking.event_date} with {booking.artist.user.first_name} {booking.artist.user.last_name} has been rejected.'

        Notification.objects.create(
            user=booking.client,
            notification_type=notification_type,
            title=title,
            description=description,
            booking=booking
        )
    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist.")

def create_booking_cancelled_notification(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        notification_type = 'booking_cancelled'
        title = 'Booking Cancelled!'
        description = f'Your booking for an event on {booking.event_date} with {booking.client.first_name} {booking.client.last_name} has been rejected.'

        Notification.objects.create(
            user=booking.client,
            notification_type=notification_type,
            title=title,
            description=description,
            booking=booking
        )
    except Booking.DoesNotExist:
        print(f"Booking with id {booking_id} does not exist.")

# def create_payment_reminder_notification(booking_id):
#     try:
#         booking = Booking.objects.get(id=booking_id)

#         notification_type = 'payment_reminder'
#         title = 'Payment Reminder!'
#         description = f'Remember to make the payment for your booking on {booking.event_date} with {booking.artist.get_full_name()}.'

#         Notification.objects.create(
#             user=booking.client,
#             notification_type=notification_type,
#             title=title,
#             description=description,
#             booking=booking
#         )
#     except Booking.DoesNotExist:
#         print(f"Booking with id {booking_id} does not exist.")


# def create_event_reminder_notification(booking_id):
#     try:
#         booking = Booking.objects.get(id=booking_id)

#         notification_type = 'event_reminder'
#         title = 'Event Reminder!'
#         description = f'Reminder: Your event with {booking.artist.get_full_name()} is on {booking.event_date}.'

#         Notification.objects.create(
#             user=booking.client,
#             notification_type=notification_type,
#             title=title,
#             description=description,
#             booking=booking
#         )
#     except Booking.DoesNotExist:
#         print(f"Booking with id {booking_id} does not exist.")
