from rest_framework.serializers import ModelSerializer
from .models import ClientDispute, ArtistDispute


class ClientDisputeSerializer(ModelSerializer):
    class Meta:
        model = ClientDispute
        fields = '__all__'

class ArtistDisputeSerializer(ModelSerializer):
    class Meta:
        model = ArtistDispute
        fields = '__all__'

