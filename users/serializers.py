from rest_framework.serializers import ModelSerializer, SerializerMethodField, DateField
from .models import Profile, UserAccount
from datetime import datetime
from artists.models import ArtistApplication


class ProfileSerializer(ModelSerializer):
    dob = DateField(input_formats=["%Y-%m-%d"])
    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['complete_address'] = f'{instance.street}, {instance.brgy}, {instance.municipality}, {instance.province}, {instance.country}'
        representation['phone'] = f'+63{instance.phone}'
        if instance.dob:
            representation['formatted_dob'] = instance.dob and instance.dob.strftime('%B, %d, %Y')
        else:
            representation['dob'] = None

        return representation

class UserAccountSerializer (ModelSerializer):
    profile = ProfileSerializer()
    has_echoee_application = SerializerMethodField()
    class Meta:

        model = UserAccount
        fields =  UserAccount
        fields =  ['id', 'email','first_name','last_name', 'is_verified', 'is_staff', 'is_active', 'role', 'profile','category','is_roled',
                   'business_permit','doc_image1','doc_image2','doc_image3','doc_image4', 'doc_image5','government_id',
                   'government_id_type','production_page','business_name','business_boost_opted','business_image','has_echoee_application'
                   ]

    def get_has_echoee_application(self, obj):
        request = self.context.get('request', None)
        if request is None:
            return False

        user = request.user
        has_echoee_application = ArtistApplication.objects.filter(user=user).exists()
        return has_echoee_application

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['fullname'] = f'{instance.first_name} {instance.last_name}'
        return representation


class UserProfileSerializer(ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = UserAccount
        fields =  ['id', 'email','first_name','last_name', 'is_verified', 'is_staff', 'is_active', 'role', 'profile',
                   'business_permit','doc_image1','doc_image2','doc_image3','doc_image4', 'doc_image5','government_id',
                   'government_id_type','production_page','business_name','business_image'
                   ]

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['fullname'] = f'{instance.first_name} {instance.last_name}'
        return representation

class ChangeNameSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['first_name','last_name']
