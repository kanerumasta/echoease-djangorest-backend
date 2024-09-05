from django.db import models
from artists.models import Artist
from django.contrib.auth import get_user_model



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


    status_choices = [
    ('pending','Pending'),
    ('cancelled','Cancelled'),
    ('approved', 'Approved'),
    ('completed','Completed')
    ]

    status = models.CharField(max_length=20, choices=status_choices, default='pending')

    class Meta:
        unique_together = ('artist','event_date','client')



    

