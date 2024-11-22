from rest_framework import serializers
from .models import Review
from users.serializers import UserAccountSerializer

class ReviewsSerializer(serializers.ModelSerializer):
    client = UserAccountSerializer(read_only=True)
    class Meta:
        model = Review
        fields = '__all__'
