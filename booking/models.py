from django.db import models
from artists.models import Artist
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from artists.models  import Rate
from django.utils import timezone
from datetime import datetime
User = get_user_model()

class Booking(models.Model):
    booking_reference = models.CharField(max_length=15, blank=True, unique=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Echoee')
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Echoer')
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    municipality = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    is_reviewed = models.BooleanField(default=False)
    decline_reason = models.TextField(null=True, blank=True)
    cancel_reason = models.TextField(null=True, blank=True)
    cancelled_by = models.CharField(null=True, blank=True, choices=[
        ('client','Client'),
        ('artist','Artist')
        ])

    status_choices = [
    ('pending','Pending'),
    ('cancelled','Cancelled'),
    ('awaiting_downpayment','Wating for Downpayment'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
    ('completed','Completed')
    ]

    status = models.CharField(max_length=20, choices=status_choices, default='pending')

    @property
    def is_event_due(self):
        # Combine event date and end time into a full datetime
        event_end_datetime = timezone.make_aware(
            datetime.combine(self.event_date, self.end_time),
            timezone.get_current_timezone()
        )
        # Compare with current time
        return timezone.now() > event_end_datetime


    #approve here only sets statust to awaiting downpayment

    def calculate_downpayment(self):
        if self.amount is None:
            return Decimal(0)
        return Decimal(0.20) * self.amount #20% downpayment

    def approve(self):
        self.status = 'awaiting_downpayment'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    #this sets the booking as ready
    def downpayment_paid(self):
        self.status = 'approved'
        #create timeslot exception for this time slot



        self.save()

    def cancel(self, cancelled_by):
        if cancelled_by not in ['client', 'artist']:
            raise ValidationError("Invalid cancellation party. Must be 'client' or 'artist'.")

        # Check if the booking can still be canceled
        if self.is_completed:
            raise ValidationError("You cannot cancel a completed booking.")

        self.status = 'cancelled'
        self.cancelled_by = cancelled_by
        self.save()

    def complete(self):
        self.status = 'completed'
        self.is_completed = True
        self.save()

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_complete(self):
        return self.status == 'completed'

    @property
    def is_cancelled(self):
        return self.status == 'cancelled'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def full_address(self):
        address_parts = [
            self.street,
            self.province,
            self.municipality,
            self.barangay
        ]
        return f'{", ".join(filter(None, address_parts))} @ {self.landmark}'


    def clean(self) -> None:
        super().clean()
        if self.start_time >= self.end_time:
            raise ValidationError("The start time must be before the end time.")

        if self.artist.user == self.client:
            raise ValidationError("Client user should not book it's own artist profile")




    def save(self, *args, **kwargs):
        self.clean()
        self.amount = self.rate.amount
        super().save(*args, **kwargs)



    def __str__(self):
        return f'{self.event_name} - {self.artist} - {self.client}'

    class Meta:
        ordering = ['-created_at']
