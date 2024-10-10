from rest_framework.serializers import ModelSerializer
from .models import DownPayment

class DownpaymentSerializer(ModelSerializer):
    class Meta:
        model = DownPayment
        fields = '__all__'
        
