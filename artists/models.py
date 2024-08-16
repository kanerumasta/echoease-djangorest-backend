from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from .validators import date_not_future

User = get_user_model()



class ArtistApplication(models.Model):
    status_choices = [
        ('under_review', 'Under Review'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ]
    sample_video1 = CloudinaryField('sample_video', resource_type='video')
    sample_video2 = CloudinaryField('sample_video',null=True, blank=True)
    sample_video3 = CloudinaryField('sample_video',null=True, blank=True)


    #Mirror ArtistProfile Fields
    dob = models.DateField(validators=[date_not_future])
    gender = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    # Contacts'
    phone = models.CharField(max_length=20)

    # Address
    street = models.CharField(max_length=255)
    brgy = models.CharField(max_length=60)
    city = models.CharField(max_length=255)  # or town
    country = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=10)

    # Photos
    # profile_pic = CloudinaryField('profile_pic',null=True, blank=True)

    cover_photo = CloudinaryField(
        'cover_photo', null=True, default=None, blank=True)
    

    # Socials
    fb_page = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    fb_profile_link = models.CharField(max_length=255, null=True, blank=True)



    status = models.CharField(max_length=50, choices=status_choices, default='under_review')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        if self.user:
            return f'Application {self.user}'
        return f'No user application {self.id}'
    


class Artist(models.Model):
    STATUS = [
        ('active','Active'),
        ('inactive', 'Inactive')
    ]
    slug = models.SlugField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10,default='active', choices=STATUS, null=True, blank=True)

    dob = models.DateField(blank=True, null=True, validators=[date_not_future])
    gender = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    # Contacts
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Address
    street = models.CharField(max_length=255, null=True, blank=True)
    brgy = models.CharField(max_length=60, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)  # or town
    country = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)

    # Photos
    # profile_pic = CloudinaryField('profile_pic',null=True, blank=True)
    cover_photo = CloudinaryField(
        'cover_photo', null=True, blank=True, default=None)

    # Socials
    fb_page = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    fb_profile_link = models.CharField(max_length=255, null=True, blank=True)



    #Relationships
    user = models.OneToOneField(User,related_name="artist",on_delete=models.CASCADE, unique=True)
    followers = models.ManyToManyField(User, related_name="artists_followed", blank=True)

    def __str__(self):
        return f'Artist-{self.user}'
    
# class ArtistProfile(models.Model):
#     dob = models.DateField(blank=True, null=True, validators=[date_not_future])
#     gender = models.CharField(max_length=20, null=True, blank=True)
#     bio = models.TextField(null=True, blank=True)

#     # Contacts
#     phone = models.CharField(max_length=20, blank=True, null=True)

#     # Address
#     street = models.CharField(max_length=255, null=True, blank=True)
#     brgy = models.CharField(max_length=60, null=True, blank=True)
#     city = models.CharField(max_length=255, null=True, blank=True)  # or town
#     country = models.CharField(max_length=255, null=True, blank=True)
#     zipcode = models.CharField(max_length=10, null=True, blank=True)

#     # Photos
#     profile_image = CloudinaryField(
#         'profile_image', null=True, default=None, blank=True)
#     cover_photo = CloudinaryField(
#         'cover_photo', null=True, blank=True, default=None)

#     # Socials
#     fb_page = models.CharField(max_length=255, null=True, blank=True)
#     instagram = models.CharField(max_length=255, null=True, blank=True)
#     twitter = models.CharField(max_length=255, null=True, blank=True)
#     fb_profile_link = models.CharField(max_length=255, null=True, blank=True)


#     # Relationships
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
    


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
