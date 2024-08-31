from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Profile, UserAccount

class UserAccountSerializer (ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'email', 'id', 'profile_image']


class VerifyProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['dob','gender', 'phone','country','province', 'municipality', 'brgy', 'zipcode']


class ProfileSerializer(ModelSerializer):
    dob = serializers.DateField(
         input_formats=['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%m/%d/%Y', '%d-%m-%Y'],
         format='%Y-%m-%d'
    )
    class Meta:
        model = Profile
        fields = '__all__'

class UserDetailSerializer(ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'profile']
    
