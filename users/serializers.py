from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Profile, UserAccount
from datetime import datetime

class UserAccountSerializer (ModelSerializer):
    class Meta:

        model = UserAccount
        fields =  ['id', 'email','first_name','last_name', 'is_verified', 'is_staff', 'is_active', 'role']

class ProfileSerializer(ModelSerializer):
    dob = serializers.DateField(input_formats=["%Y-%m-%d"])
    class Meta:
        model = Profile
        fields = '__all__'




class UserProfileSerializer(ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = UserAccount
        fields =  ['id', 'email','first_name','last_name', 'is_verified', 'is_staff', 'is_active', 'role', 'profile']