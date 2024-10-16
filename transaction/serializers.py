from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['formatted_created_at'] = instance.created_at and instance.created_at.strftime('%b %d, %Y %I:%M %p')
        representation['transaction'] = instance.get_transaction_type_display()
        return representation
