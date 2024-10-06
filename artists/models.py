
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from .validators import date_not_future
from decimal import Decimal

User = get_user_model()

class IDType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name




class ArtistApplication(models.Model):
    bio = models.TextField(null=True, blank=True)
    sample_video1 = models.FileField(upload_to="videos/", null=True, blank=True)
    sample_video2 = models.FileField(upload_to="videos/", null=True, blank=True)
    sample_video3 = models.FileField(upload_to="videos/", null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    fb_link = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status_choices = [
        ('under_review', 'Under Review'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ]

    status = models.CharField(max_length=50, choices=status_choices, default='under_review')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    #new
    idol = models.CharField(max_length=255, null=True, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)
    spotify =models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)

    award_image1 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    award_image2 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    award_image3 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    id_type = models.ForeignKey(IDType, on_delete=models.SET_NULL, null=True, blank=True)
    front_id = models.ImageField(upload_to="images/", null=True, blank=True)
    back_id = models.ImageField(upload_to="images/", null=True, blank=True)

    def __str__(self):
        if self.user:
            return f'Application {self.user}'
        return f'No user application {self.pk}'


class Artist(models.Model):
    bio = models.TextField(null=True, blank=True)
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

    #new fields
    spotify =models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    idol = models.CharField(max_length=255, null=True, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)
    award_image1 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    award_image2 = models.ImageField(upload_to="images/awards", null=True, blank=True)
    award_image3 = models.ImageField(upload_to="images/awards", null=True, blank=True)

    connections= models.ManyToManyField('self', symmetrical=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'.title()



class Portfolio(models.Model):
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE, related_name="portfolio", null=True)

    def __str__(self):
        return f'Portfolio-{self.artist.user}' # type: ignore


class PortfolioItem(models.Model):

    GROUPS = [
        ('portfolio','Portfolio'),
        ('event','Event'),
    ]


    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items", null=True)
    title = models.CharField(max_length = 255, null=True, blank=True)
    description = models.CharField(max_length = 255, null=True, blank=True)
    group = models.CharField(max_length=50,default="portfolio",choices=GROUPS,null=True, blank=True)

    #LIMIT TWO VIDEOS AND 5 IMAGES
    video1 = models.FileField(upload_to="videos/",null=True, blank=True)
    video2 = models.FileField(upload_to="videos/",null=True, blank=True)

    image1 = models.ImageField(upload_to="images/", null=True, blank=True)
    image2 = models.ImageField(upload_to="images/", null=True, blank=True)
    image3 = models.ImageField(upload_to="images/", null=True, blank=True)
    image4 = models.ImageField(upload_to="images/", null=True, blank=True)
    image5 = models.ImageField(upload_to="images/", null=True, blank=True)


class Rate(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_rates', null=True, blank=True)
    artist_application = models.ForeignKey(ArtistApplication, on_delete=models.CASCADE, related_name='rates', null=True, blank=True)
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.artist}-{self.name}-{self.amount}'

class TimeSlot(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.artist}: {self.start_time} - {self.end_time}"

    def clean(self):
        # Check for overlapping time slots
        if TimeSlot.objects.filter(artist=self.artist, start_time__lt=self.end_time, end_time__gt=self.start_time).exists():
            raise ValidationError("This time slot overlaps with an existing time slot.")

    class Meta:
        ordering = ['start_time']
        unique_together = ('artist', 'start_time', 'end_time')

class TimeSlotException(models.Model):
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f'{self.date}==>{self.time_slot}'


#this will override default timeslot
class SpecialTimeSlot(models.Model):
    date = models.DateField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time=models.TimeField()

    def __str__(self) -> str:
        return f'{self.date}-{self.artist}-{self.start_time}-{self.end_time}'
    class Meta:
        ordering = ['start_time']




class ConnectionRequest(models.Model):
    sender = models.ForeignKey(Artist,related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Artist,related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('sender', 'receiver')

    def clean(self):
        if ConnectionRequest.objects.filter(sender = self.receiver , receiver = self.sender).exists():
            raise ValidationError("A connection request between these two artists already exists.")

    def save(self, *args, **kwargs):
        self.clean()
        super(ConnectionRequest,self).save(*args, **kwargs)

    def accept(self):
        self.sender.connections.add(self.receiver)
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()


    def __str__(self):
        return f'{self.sender} to {self.receiver} - {self.status}'
