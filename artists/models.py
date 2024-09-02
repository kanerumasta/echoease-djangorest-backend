from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from .validators import date_not_future

User = get_user_model()



class Genre(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class ArtistApplication(models.Model):
 
    sample_video1 = models.FileField(upload_to="videos/", null=True, blank=True)
    sample_video2 = models.FileField(upload_to="videos/", null=True, blank=True)
    sample_video3 = models.FileField(upload_to="videos/", null=True, blank=True)

    genres = models.ManyToManyField(Genre, blank=True)


    # Socials
    fb_link = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    # fb_profile_link = models.CharField(max_length=255, null=True, blank=True)


    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    status_choices = [
        ('under_review', 'Under Review'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ]

    status = models.CharField(max_length=50, choices=status_choices, default='under_review')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        if self.user:
            return f'Application {self.user}'
        return f'No user application {self.id}'
    

class Artist(models.Model):
    slug = models.SlugField(max_length=255, blank=True, null=True)
    
    genres = models.ManyToManyField(Genre, blank=True)

    # Socials
    fb_link = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)

    STATUS = [
        ('active','Active'),
        ('inactive', 'Inactive')
    ]
    status = models.CharField(max_length=10,default='active', choices=STATUS, null=True, blank=True)



    #Relationships
    user = models.OneToOneField(User,related_name="artist",on_delete=models.CASCADE, unique=True)
    followers = models.ManyToManyField(User, related_name="artists_followed", blank=True)

    date_approved = models.DateField(null=True, blank=True)
    time_approved = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'Artist-{self.user}'
    


class Portfolio(models.Model):
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE, related_name="portfolio", null=True)

    def __str__(self):
        return f'Portfolio-{self.artist.user}' # type: ignore
    

class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items", null=True)
    title = models.CharField(max_length = 255, null=True, blank=True)
    description = models.CharField(max_length = 255, null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    file = CloudinaryField('file',resource_type = 'auto',null=True)

    def __str__(self):
        return f'PortfolioItem-{self.portfolio.id}-{self.id}' # type: ignore
