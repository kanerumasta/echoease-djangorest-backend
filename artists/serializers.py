from django.db.models import Q
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import PortfolioItemMedia ,Portfolio, PortfolioItem, Portfolio, Artist, ArtistApplication, Genre, IDType, Rate, ConnectionRequest
from django.utils.dateformat import time_format

class PortfolioItemMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItemMedia
        fields = '__all__'

class PortfolioItemSerializer(serializers.ModelSerializer):
    medias = PortfolioItemMediaSerializer(many=True, read_only=True)
    class Meta:
        model = PortfolioItem
        fields = '__all__'



class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(read_only=True,many=True)
    class Meta:
        model = Portfolio
        fields = '__all__'



class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model= Genre
        fields = '__all__'


class RateSerializer (serializers.ModelSerializer):
    class Meta:
        model =Rate
        fields = ["id","amount","name", "artist_application", "artist","description"]

class ArtistSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    artist_rates = RateSerializer(read_only=True, many=True)
    genres = GenreSerializer(many=True)

    class Meta:
        model = Artist
        fields = '__all__'

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['rates'] = representation.pop('artist_rates')
        return representation


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



class RecommendedArtistSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    genres = GenreSerializer(many=True)
    mutual = serializers.SerializerMethodField()
    class Meta:
        model = Artist
        fields = ['id','user','genres','mutual','slug']

    def get_mutual(self, obj):
        current_artist = self.context['current_artist']
        mutual_connections = current_artist.connections.filter(
            id__in = obj.connections.all()
        )
        return ArtistSerializer(mutual_connections, many=True).data
