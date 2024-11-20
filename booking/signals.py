from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from django.conf import settings
import requests
from logs.models import TransactionLogs

@receiver(post_save, sender=Booking)
def setLatLong(sender, instance, created, **kwargs):
    if created:
        url = settings.DISTANCE_MATRIX_API_URL
        key = settings.DISTANCE_MATRIX_API_KEY
        address = f'{instance.street}, {instance.barangay}, {instance.municipality}, {instance.province}, Philippines'
        params = {
            "address":address,
            "key":key,
        }
        print('PARAMS', params)
        try:
            response = requests.post(url,params=params)
            data = response.json()
            lat = data['result'][0]['geometry']['location']['lat']
            long = data['result'][0]['geometry']['location']['lng']
            instance.latitude = lat
            instance.longitude = long
            instance.save()
        except Exception as e:
            print(f'Error fetching latitude and longitude: {str(e)}')
            return

@receiver(post_save, sender = Booking)
def generate_booking_reference(sender, instance, created, **kwargs):
    if created and not instance.booking_reference:
        instance.booking_reference = f"BKG{instance.id:06d}"
        instance.save()
@receiver(post_save, sender = Booking)
def log_booking(sender, instance, created, **kwargs):
    transaction_type = 'BOOKING'
    if created:
        try:
            TransactionLogs.objects.create(
                transaction_type=transaction_type,
                message=f"New booking created {instance.pk} by {instance.client.first_name}{instance.client.last_name} : artist:{instance.artist.user.first_name} {instance.artist.user.last_name}"
            )
        except Exception as e:
            print('Error logging', e)
    else:
        try:
            TransactionLogs.objects.create(
                transaction_type=transaction_type,
                message=f"Booking {instance.pk} status updated to {instance.status}"
            )
        except Exception as e:
            print("Error logging", e)
