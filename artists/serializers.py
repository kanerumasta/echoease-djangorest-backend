
from rest_framework import serializers

from .models import PortfolioItem, Portfolio, Artist, ArtistApplication, Genre
from users.serializers import UserDetailSerializer, UserAccountSerializer

class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id','portfolio','title','description','file_type','file']
    def create(self, validated_data):
        id = validated_data.pop('id', None)
        instance = self.Meta.model(**validated_data)
        if id is not None:
            instance.id = id 
        instance.save()
        return instance

    


class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(read_only=True,many=True)
    class Meta:
        model = Portfolio
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model= Genre
        fields = '__all__'



class ArtistSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
    class Meta:
        model = Artist
        fields = '__all__'



class ArtistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class ArtistApplicationSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), 
        many=True, 
    )
    class Meta:
        model = ArtistApplication
        fields = '__all__'

class FollowArtistSerializer(serializers.Serializer):
    artist_id = serializers.IntegerField()
