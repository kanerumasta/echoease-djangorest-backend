from django.db.models import Q
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import PortfolioItemMedia ,Portfolio, PortfolioItem, Portfolio, Artist, ArtistApplication, Genre, IDType, Rate, ConnectionRequest
from django.utils.dateformat import time_format
from datetime import datetime
from django.utils import timezone


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
        fields = ["id","amount","name", "artist","description"]

class ArtistSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    is_available = serializers.SerializerMethodField()
    artist_rates = RateSerializer(read_only=True, many=True)
    genres = GenreSerializer(many=True)
    portfolio = serializers.PrimaryKeyRelatedField(read_only=True)
    is_new = serializers.SerializerMethodField()
    class Meta:
        model = Artist
        fields = '__all__'

    def get_is_new(self, obj):
        return obj.created_at >=  timezone.now() - timezone.timedelta(days=1)

    def get_is_available(self, obj):
        has_sched = obj.availabilities.exists() or obj.recurring_availabilities.exists()
        return has_sched


    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['rates'] = representation.pop('artist_rates')
        return representation


# class ArtistApplicationSerializer(serializers.ModelSerializer):

#     genres = serializers.PrimaryKeyRelatedField(
#         queryset=Genre.objects.all(),
#         many=True,
#     )
#     class Meta:
#         model = ArtistApplication
#         fields = '__all__'

#     def create(self, validated_data):

#         user = validated_data.pop('user')
#         genres = validated_data.pop('genres',[])
#         application = ArtistApplication.objects.create(user=user, **validated_data)
#         application.genres.set(genres)

#         return application


#  bio = models.TextField(null=True, blank=True)
#     slug = models.SlugField(max_length=255, blank=True, null=True)
#     genres = models.ManyToManyField(Genre, blank=True)
#     stage_name = models.CharField(max_length=255, null=True, blank=True)


#     # Socials
#     fb_link = models.CharField(max_length=255, null=True, blank=True)
#     instagram = models.CharField(max_length=255, null=True, blank=True)
#     twitter = models.CharField(max_length=255, null=True, blank=True)
#     status = models.CharField(max_length=10,default='active', choices=STATUS, null=True, blank=True)
#     #Relationships
#     user = models.OneToOneField(User,related_name="artist",on_delete=models.CASCADE, unique=True)
#     followers = models.ManyToManyField(User, related_name="artists_followed", blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     #new fields
#     spotify =models.CharField(max_length=255, null=True, blank=True)
#     youtube = models.CharField(max_length=255, null=True, blank=True)
#     idol = models.CharField(max_length=255, null=True, blank=True)
#     years_experience = models.IntegerField(null=True, blank=True)
#     award_image1 = models.ImageField(upload_to="images/awards", null=True, blank=True)
#     award_image2 = models.ImageField(upload_to="images/awards", null=True, blank=True)
#     award_image3 = models.ImageField(upload_to="images/awards", null=True, blank=True)

#     connections= models.ManyToManyField('self', symmetrical=True, blank=True)

#     #BANK DETAIL
#     channel_code = models.CharField(max_length=20, null=True, blank=True)
#     account_holder_name = models.CharField(max_length=255, null=True, blank=True)
#     encrypted_account_number = models.BinaryField(max_length=255,null=True, blank=True)

class ArtistApplicationSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
    )

    class Meta:
        model = Artist
        fields = [
            'bio','slug','genres','stage_name','user',"id",
            'fb_link','instagram','twitter','spotify','youtube',
            'channel_code','account_holder_name','account_number',
        ]

    def create(self, validated_data):
        user = validated_data.pop('user')
        genres = validated_data.pop('genres',[])

        artist = Artist.objects.create(user=user, **validated_data)
        artist.genres.set(genres)

        return artist

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
