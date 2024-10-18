from rest_framework.serializers import ModelSerializer
from .models import ClientDispute, ArtistDispute, Dispute, DisputeEvidence


class ClientDisputeSerializer(ModelSerializer):
    class Meta:
        model = ClientDispute
        fields = '__all__'

class ArtistDisputeSerializer(ModelSerializer):
    class Meta:
        model = ArtistDispute
        fields = '__all__'

class DisputeSerializer(ModelSerializer):
    class Meta:
        model =  Dispute
        fields = '__all__'

class DisputeEvidenceSerializer(ModelSerializer):
    class Meta:
        model = DisputeEvidence
        fields = '__all__'
