
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import PortfolioItem, Portfolio, Artist, ArtistApplication, Genre, IDType, Rate, ConnectionRequest, TimeSlot, TimeSlotException, SpecialTimeSlot
from django.utils.dateformat import time_format


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = '__all__'



class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(read_only=True,many=True)
    class Meta:
        model = Portfolio
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for item in representation.get('items', []):
            # Include video field names with their URLs
            videos = [
                {"field": "video1", "url": item.get('video1')},
                {"field": "video2", "url": item.get('video2')}
            ]
            # Filter out videos where URL is None
            item['videos'] = [video for video in videos if video["url"] is not None]

            # Include image field names with their URLs
            images = [
                {"field": "image1", "url": item.get('image1')},
                {"field": "image2", "url": item.get('image2')},
                {"field": "image3", "url": item.get('image3')},
                {"field": "image4", "url": item.get('image4')},
                {"field": "image5", "url": item.get('image5')}
            ]
            # Filter out images where URL is None
            item['images'] = [image for image in images if image["url"] is not None]
        return representation
        # representation =  super().to_representation(instance)
        # for item in representation.get('items',[]):
        #     item['videos'] = [video for video in [item.pop('video1'), item.pop('video2')] if video is not None]
        #     item['images'] = [image for image in [item.pop('image1'), item.pop('image2'), item.pop('image3'), item.pop('image4'), item.pop('image5')] if image is not None]
        # return representation


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model= Genre
        fields = '__all__'


class RateSerializer (serializers.ModelSerializer):
    class Meta:
        model =Rate
        fields = ["id","amount","name", "artist_application", "artist"]

class ArtistSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    genres = GenreSerializer(many=True)
    class Meta:
        model = Artist
        fields = ['id','bio', 'slug','genres','fb_link','instagram','twitter','status','user','followers','date_approved','time_approved', 'spotify', 'youtube',
                  'idol','years_experience','award_image1','award_image2','award_image3','portfolio', 'connections']


class ArtistApplicationSerializer(serializers.ModelSerializer):

    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
    )
    class Meta:
        model = ArtistApplication
        fields = '__all__'

    def create(self, validated_data):

        user = validated_data.pop('user')
        genres = validated_data.pop('genres',[])
        application = ArtistApplication.objects.create(user=user, **validated_data)
        application.genres.set(genres)

        return application

class IDTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDType
        fields = '__all__'

class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        write_only=True
    )
    receiver = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        write_only=True
    )
    sender_details = ArtistSerializer(source='sender', read_only=True)
    receiver_details = ArtistSerializer(source='receiver', read_only=True)


    class Meta:
        model = ConnectionRequest
        fields = '__all__'


    def to_representation(self, instance):
        rep =  super().to_representation(instance)
        rep['sender'] = rep.pop('sender_details')
        rep['receiver'] = rep.pop('receiver_details')
        return rep

class ArtistConnectionsSerializer(serializers.ModelSerializer):
    connections = ArtistSerializer(many=True, read_only=True)
    class Meta:
        model = Artist
        fields =['connections']


class TimeSlotSerializer (serializers.ModelSerializer):
    class Meta:
        model=TimeSlot
        fields = '__all__'

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        artist = attrs.get('artist')

        # Ensure start_time is less than end_time
        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be less than end time.")

        # Check for overlapping time slots
        existing_slots = TimeSlot.objects.filter(
            artist=artist,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if existing_slots.exists():
            raise serializers.ValidationError("This time slot overlaps with an existing time slot.")

        return attrs
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['start_time'] = time_format(instance.start_time, 'h:i A')
        representation['end_time'] = time_format(instance.end_time, 'h:i A')
        return representation


class TimeslotExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlotException
        fields = '__all__'


class SpecialTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialTimeSlot
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['start_time'] = time_format(instance.start_time, 'h:i A')
        representation['end_time'] = time_format(instance.end_time, 'h:i A')
        return representation
