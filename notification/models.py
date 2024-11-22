from django.db import models
from artists.models import Artist
from booking.models import Booking
from django.conf import settings



class Notification(models.Model):
    notification_choices = [
        ('booking_rejected', 'Booking Rejected'),
        ('booking_confirmation', 'Booking Confirmation'),
        ('new_booking', 'New Booking'),
        ('booking_cancelled', 'Booking Cancelled'),

        ('downpayment_paid', 'Down Payment Paid'),
        ('dibursement_received', 'Dibursement Received'),
        ('refund_received', 'Refund Received'),


        ('message', 'Message'),

        ('new_follower', 'New Follower'),

        ('connection_request_accepted', 'Connection Request Accepted'),
        ('connection_request_rejected', 'Connection Request Rejected'),
        ('connection_request_sent', 'Connection Request Sent'),

        ('payment_reminder', 'Payment Reminder'),
        ('event_reminder', 'Event Reminder'),

        ('application_accepted', 'Application Accepted'),
        ('reputation', 'Reputation'),
        ('admin', 'Admin'),
        ('warning', 'Warning'),
        ('reports', 'Reports'),

    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, related_name='booking_notifications')
    notification_type = models.CharField(max_length=50, choices=notification_choices)
    title = models.CharField(max_length=255)
    description = models.TextField()

    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=255,null=True, blank=True)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="notifications_as_follower", on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def read(self):
        self.is_read = True
        self.save()

    class Meta:
        ordering = ['is_read','-created_at']
