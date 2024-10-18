from rest_framework.serializers import ModelSerializer
from .models import Dispute, DisputeEvidence

class DisputeSerializer(ModelSerializer):
    class Meta:
        model =  Dispute
        fields = '__all__'

class DisputeEvidenceSerializer(ModelSerializer):
    class Meta:
        model = DisputeEvidence
        fields = '__all__'
