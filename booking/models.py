from django.db import models
from artists.models import Artist
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from artists.models  import Rate


User = get_user_model()

class Booking(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Echoee')
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Echoer')


    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    event_time = models.TimeField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    rate = models.ForeignKey(Rate, on_delete=models.CASCADE, null=True, blank=True)

    province = models.CharField(max_length=255, null=True, blank=True)
    municipality = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)



    status_choices = [
    ('pending','Pending'),
    ('cancelled','Cancelled'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
    ('completed','Completed')
    ]

    status = models.CharField(max_length=20, choices=status_choices, default='pending')


    def approve(self):
        self.status = 'approved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def cancel(self):
        self.status = 'cancelled'
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
        if self.artist.user == self.client:
            raise ValidationError("Client user should not book it's own artist profile")


    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-event_date']
