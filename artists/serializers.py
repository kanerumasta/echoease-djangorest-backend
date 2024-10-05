
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import PortfolioItem, Portfolio, Artist, ArtistApplication, Genre, IDType, Rate, ConnectionRequest


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
        representation =  super().to_representation(instance)
        for item in representation.get('items',[]):
            item['videos'] = [video for video in [item.pop('video1'), item.pop('video2')] if video is not None]
            item['images'] = [image for image in [item.pop('image1'), item.pop('image2'), item.pop('image3'), item.pop('image4'), item.pop('image5')] if image is not None]
        return representation


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
