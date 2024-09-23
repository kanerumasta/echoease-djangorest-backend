
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import PortfolioItem, Portfolio, Artist, ArtistApplication, Genre, IDType, Rate

    # portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items", null=True)
    # title = models.CharField(max_length = 255, null=True, blank=True)
    # description = models.CharField(max_length = 255, null=True, blank=True)
    # group = models.CharField(max_length=50,default="portfolio",choices=GROUPS,null=True, blank=True)

    # #LIMIT TWO VIDEOS AND 5 IMAGES
    # video1 = models.FileField(upload_to="videos/",null=True, blank=True),
    # video2 = models.FileField(upload_to="videos/",null=True, blank=True),

    # image1 = models.ImageField(upload_to="images/", null=True, blank=True)
    # image2 = models.ImageField(upload_to="images/", null=True, blank=True)
    # image3 = models.ImageField(upload_to="images/", null=True, blank=True)
    # image4 = models.ImageField(upload_to="images/", null=True, blank=True)
    # image5 = models.ImageField(upload_to="images/", null=True, blank=True)


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = '__all__'


    # def create(self, validated_data):
    #     id = validated_data.pop('id', None)
    #     instance = self.Meta.model(**validated_data)
    #     if id is not None:
    #         instance.pk = id 
    #     instance.save()
    #     return instance


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



#ARTISTS
    # bio = models.TextField(null=True, blank=True)
    # slug = models.SlugField(max_length=255, blank=True, null=True)
    # genres = models.ManyToManyField(Genre, blank=True)
    # fb_link = models.CharField(max_length=255, null=True, blank=True)
    # instagram = models.CharField(max_length=255, null=True, blank=True)
    # twitter = models.CharField(max_length=255, null=True, blank=True)
    # rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    # status = models.CharField(max_length=10,default='active', choices=STATUS, null=True, blank=True)
    # user = models.OneToOneField(User,related_name="artist",on_delete=models.CASCADE, unique=True)
    # followers = models.ManyToManyField(User, related_name="artists_followed", blank=True)
    # date_approved = models.DateField(null=True, blank=True)
    # time_approved = models.TimeField(null=True, blank=True)
    # spotify =models.CharField(max_length=255, null=True, blank=True)
    # youtube = models.CharField(max_length=255, null=True, blank=True)
    # idol = models.CharField(max_length=255, null=True, blank=True)
    # years_experience = models.IntegerField(null=True, blank=True)
    # award_image1 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    # award_image2 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    # award_image3 = models.ImageField(upload_to="images/awards", null=True, blank=True)



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
                  'idol','years_experience','award_image1','award_image2','award_image3','portfolio']




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