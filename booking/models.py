from django.db import models
from artists.models import Artist
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal


User = get_user_model()

class Booking(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    event_time = models.TimeField()
    duration_in_hours = models.IntegerField(null=True, blank=True)
    duration_in_minutes = models.IntegerField(null=True, blank=True)
    event_location = models.CharField(max_length=255)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))



    status_choices = [
    ('pending','Pending'),
    ('cancelled','Cancelled'),
    ('approved', 'Approved'),
    ('completed','Completed')
    ]

    status = models.CharField(max_length=20, choices=status_choices, default='pending')

    class Meta:
        unique_together = ('artist','event_date')

    def complete_booking (self):
        self.is_completed = True
        self.save()

    @property
    def is_confirmed(self):
        return self.status == 'approved'

    def clean(self) -> None:
        
        super().clean()
        if self.artist.user == self.client:
            raise ValidationError("Client user should not book it's own artist profile")
    

    def save(self, *args, **kwargs):
        self.clean()
        self.amount = self.artist.rate
        super().save(*args, **kwargs)


    

