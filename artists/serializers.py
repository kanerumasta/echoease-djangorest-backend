
from rest_framework import serializers

from .models import PortfolioItem, Portfolio, Artist, ArtistApplication
from users.serializers import UserDetailSerializer

class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id','portfolio','title','description','file_type','file']
    def create(self, validated_data):
        id = validated_data.pop('id', None)
        instance = self.Meta.model(**validated_data)
        if id is not None:
            instance.id = id # type: ignore
        instance.save()
        return instance

    


class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(read_only=True,many=True)
    class Meta:
        model = Portfolio
        fields = '__all__'




class ArtistSerializer(serializers.ModelSerializer):
    # user = UserDetailSerializer(read_only=True)
    class Meta:
        model = Artist
        fields = '__all__'



class ArtistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class ArtistApplicationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ArtistApplication
        fields = '__all__'

class FollowArtistSerializer(serializers.Serializer):
    artist_id = serializers.IntegerField()
