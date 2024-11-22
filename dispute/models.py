from django.db import models
from booking.models import Booking
from django.conf import settings
from artists.models import Artist



USER = settings.AUTH_USER_MODEL


class Dispute(models.Model):
    dispute_type = models.CharField(max_length=50, choices=[
        ('artist','Artist'),
        ('client', 'Client')
        ])
    booking =  models.ForeignKey(Booking,on_delete=models.CASCADE, related_name="disputes")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(USER, on_delete=models.CASCADE, null=True, blank=True)
    DISPUTE_STATUS = [
        ('open','Open'),
        ('closed','Closed'),
        ('cancelled','Cancelled'),
        ('under_review','Under Review'),
        ('resolved','Resolved'),
        ('escalated','Escalated'),
    ]
    reason = models.CharField(max_length=100,default='other', choices = [
        ('performance_quality','Performance Quality'),
        ('cancellation','Cancellation'),
        ('no_show','No Show'),
        ('miscommunication','Miscommunication'),
        ('other','Other'),
    ])
    status = models.CharField(choices=DISPUTE_STATUS, default='under_review')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    date_resolved = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.booking}-{self.dispute_type}'

class DisputeEvidence(models.Model):
    media_type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='evidences')
    file = models.FileField(upload_to='dispute_evidences/')





class ArtistDispute(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='artist_disputes')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    DISPUTE_STATUS = [
        ('open','Open'),
        ('closed','Closed'),
        ('under_review','Under Review'),
        ('resolved','Resolved'),
        ('escalated','Escalated'),
    ]
    status = models.CharField(choices=DISPUTE_STATUS, default='under_review')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    DISPUTE_REASON = [
        ('performance_quality','Performance Quality'),
        ('cancellation','Cancellation'),
        ('no_show','No Show'),
        ('miscommunication','Miscommunication'),
        ('other','Other'),
    ]
    reason = models.CharField(max_length=50,choices=DISPUTE_REASON)
    description =  models.TextField()

    is_resolved = models.BooleanField(default=False)

    date_resolved = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)






class ClientDispute(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='client_disputes')
    client = models.ForeignKey(USER, on_delete=models.CASCADE)


    DISPUTE_STATUS = [
        ('open','Open'),
        ('closed','Closed'),
        ('under_review','Under Review'),
        ('resolved','Resolved'),
        ('escalated','Escalated'),

    ]


    status = models.CharField(max_length=50,choices=DISPUTE_STATUS, default='under_review')
    date_created = models.DateTimeField(auto_now_add=True)

    DISPUTE_REASON = [
        ('performance_quality','Performance Quality'),
        ('cancellation','Cancellation'),
        ('no_show','No Show'),
        ('miscommunication','Miscommunication'),
        ('other','Other'),
    ]
    reason = models.CharField(max_length=50,choices=DISPUTE_REASON)
    description =  models.TextField()

    is_resolved = models.BooleanField(default=False)
    date_resolved = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
