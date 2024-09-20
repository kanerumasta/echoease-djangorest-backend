from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Profile, UserAccount
from datetime import datetime

class ProfileSerializer(ModelSerializer):
    dob = serializers.DateField(input_formats=["%Y-%m-%d"])
    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['complete_address'] = f'{instance.street}, {instance.brgy}, {instance.municipality}, {instance.province}, {instance.country}'
        return representation

class UserAccountSerializer (ModelSerializer):
    profile = ProfileSerializer()
    class Meta:

        model = UserAccount
        fields =  ['id', 'email','first_name','last_name', 'is_verified', 'is_staff', 'is_active', 'role', 'profile']

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['fullname'] = f'{instance.first_name} {instance.last_name}'
        return representation


class UserProfileSerializer(ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = UserAccount
        fields =  ['id', 'email','first_name','last_name', 'is_verified', 'is_staff', 'is_active', 'role', 'profile']

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['fullname'] = f'{instance.first_name} {instance.last_name}'
        return representation