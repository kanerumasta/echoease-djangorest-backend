from celery import shared_task
from django.utils import timezone
from .models import Booking
from django.core.mail import send_mail
import logging
from django.conf import settings
from notification.models import Notification
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@shared_task
def send_payment_reminders():
    due_bookings = Booking.objects.filter(is_completed=False, has_sent_payment_reminder=False, status='approved')
    for booking in due_bookings:
        if booking.is_event_due:
            logger.info(f"Sending payment reminder for booking {booking.booking_reference}")
            subject = f"Payment Reminder for Booking {booking.booking_reference}"
            message = f"Dear {booking.client.full_name},\n\n" \
                    f"This is a reminder that your payment for the booking of '{booking.event_name}' " \
                    f"on {booking.event_date} is due. Please ensure that your payment is completed." \
                    f"\n\nThank you!"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.client.email]) # type: ignore
            booking.has_sent_payment_reminder = True
            booking.save()

            Notification.objects.create(
                user = booking.client,
                notification_type = 'payment_reminder',
                title=f"Payment Reminder for Booking {booking.booking_reference}",
                description=message,
                booking=booking
            )

@shared_task
def expire_bookings(): #expire bookings that are not approved by artists
    two_days_ago = datetime.now() - timedelta(days=2)#TODO edit this to two days
    expired_bookings = Booking.objects.filter(is_completed=False, status='pending', created_at__lt=two_days_ago.date())
    for booking in expired_bookings:

        logger.info(f"Expiring booking {booking.booking_reference}")
        logger.info(f"kani {booking.booking_reference}")
        booking.status = 'expired'
        booking.is_expired = True
        booking.save()
