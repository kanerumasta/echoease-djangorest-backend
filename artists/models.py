from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.utils.text import slugify


class Artist(models.Model):
    slug = models.SlugField(max_length=255, blank=True, null=True)
    stage_name = models.CharField(max_length=50, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    #Relationships
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name="artist",on_delete=models.CASCADE, unique=True)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="artists_followed", blank=True)

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
