
from booking.models import Booking
from notification.models import Notification
# utils.py
# from weasyprint import HTML
# from django.template.loader import render_to_string
from django.conf import settings
import os

# def generate_booking_pdf(booking):
#     # Load HTML template and pass booking data
#     html_string = render_to_string('pdf_templates/booking_pdf.html', {'booking': booking})

#     # Generate the PDF file
#     html = HTML(string=html_string)
#     pdf_file = html.write_pdf()

#     # You can store the PDF temporarily in your MEDIA_ROOT
#     pdf_filename = f'booking_{booking.booking_reference}.pdf'
#     pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

#     # Save PDF to file
#     with open(pdf_path, 'wb') as f:
#         f.write(pdf_file)

#     return pdf_path



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
        description = f'Your booking for an event on {booking.event_date} with {booking.artist.user.first_name} {booking.artist.user.last_name} has been confirmed. Mangayo mi ug downpayment lods.'

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
#BUSINESS BOOST
def upload_event_to_facebook():
    pass
