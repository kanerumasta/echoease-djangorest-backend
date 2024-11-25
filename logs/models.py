from django.db import models
from booking.models import Booking
from payment.models import Payment


class UserLogs(models.Model):
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    action = models.CharField(max_length=60)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

class TransactionLogs (models.Model):
    transaction_type = models.CharField(max_length=60)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return f"{self.message} - {self.timestamp}"
