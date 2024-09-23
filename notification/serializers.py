from rest_framework.serializers import ModelSerializer
from .models import Notification
from users.serializers import UserAccountSerializer
from booking.serializers import BookingSerializer
from chat.serializers import MessageSerializer


class NotificationSerializer(ModelSerializer):
    user = UserAccountSerializer(read_only=True)
    follower = UserAccountSerializer(read_only=True)
    booking = BookingSerializer(read_only=True)
    message = MessageSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = '__all__'

    