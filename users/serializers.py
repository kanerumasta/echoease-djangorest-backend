from rest_framework.serializers import ModelSerializer
from .models import ClientProfile, UserAccount

class UserAccountSerializer (ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'email', 'id']


class VerifyProfileSerializer(ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['dob','gender', 'phone','street','brgy', 'city', 'country', 'zipcode']


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = '__all__'

class UserDetailSerializer(ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'profile']
    
