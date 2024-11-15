from rest_framework import serializers
from .models import Transaction
from booking.serializers import BookingSerializer
from payment.serializers import PaymentSerializer
class TransactionSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['formatted_created_at'] = instance.created_at and instance.created_at.strftime('%b %d, %Y %I:%M %p')
        representation['formatted_date'] = instance.created_at and instance.created_at.strftime('%b %d, %Y')
        representation['formatted_time'] = instance.created_at and instance.created_at.strftime('%I:%M %p')
        representation['transaction'] = instance.get_transaction_type_display()
        return representation
