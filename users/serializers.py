from rest_framework.serializers import ModelSerializer
from django.conf import settings
from .models import Profile

class UserAccountSerializer (ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['first_name', 'last_name', 'email', 'id']


class VerifyProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['dob','gender', 'phone','street','brgy', 'city', 'country', 'postal_code']