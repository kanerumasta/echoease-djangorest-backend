from django.db import models
from artists.models import Artist
from booking.models import Booking
from django.conf import settings



class Notification(models.Model):
    notification_choices = [
        ('admin', 'Admin'),
        ('message', 'Message'),
        ('application_accepted', 'Application Accepted'),
        ('new_booking', 'New Booking'),
        ('new_follower', 'New Follower'),
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_rejected', 'Booking Rejected'),
        ('payment_reminder', 'Payment Reminder'),
        ('event_reminder', 'Event Reminder'),
        ('downpayment_paid', 'Down Payment Paid'),
        ('dibursement_received', 'Dibursement Received'),

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
