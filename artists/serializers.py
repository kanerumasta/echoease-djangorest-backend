
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import PortfolioItem, Portfolio, Artist, ArtistApplication, Genre, IDType

class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id','portfolio','title','description','file_type','file']
    def create(self, validated_data):
        id = validated_data.pop('id', None)
        instance = self.Meta.model(**validated_data)
        if id is not None:
            instance.pk = id 
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
    user = UserProfileSerializer()
    genres = GenreSerializer(many=True)
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