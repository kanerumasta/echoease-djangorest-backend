from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    event_date = serializers.DateField(input_formats=["%m/%d/%Y"])
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['client']