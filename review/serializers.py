from rest_framework import serializers
from .models import Review
from users.serializers import UserAccountSerializer

class ReviewsSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=UserAccountSerializer.Meta.model.objects.all(),
        source='client',
        write_only=True
    )  # Used for posting new data

    class Meta:
        model = Review
        fields = '__all__'

    def get_client(self, obj):
        return UserAccountSerializer(obj.client).data
