from django.db import models
from booking.models import Booking
from django.conf import settings

USER = settings.AUTH_USER_MODEL
class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    client = models.ForeignKey(USER, on_delete=models.CASCADE, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('booking','client')

    def __str__(self):
        return f"Review for booking {self.booking.booking_reference}"
