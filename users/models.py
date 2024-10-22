from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from cryptography.fernet import Fernet
from django.conf import settings

from .validators import date_not_future

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):

        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        email = email.lower()
        user = self.model(
            email=email,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):

        user = self.create_user(
            email,
            password=password,
            **kwargs
        )

        user.is_staff = True
        user.is_superuser = True
        user.role = "admin"
        user.save(using=self._db)
        return user




class UserAccount(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    business_boost_opted = models.BooleanField(default=False)


    # Roles
    Roles = (('artist', 'Artist'), ('client', 'Client'), ('admin', 'Admin'))
    role = models.CharField(choices=Roles, default='client',
                            max_length=20, null=True, blank=True)
    joined = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)
    Categories = (('bar_owner', 'Bar Owner'), ('regular', 'Regular'), ('event_organizer', 'Event Organizer'))
    category = models.CharField(max_length=50,choices=Categories, default='regular')
    is_roled = models.BooleanField(default=False)
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_image = models.ImageField(upload_to='images/',null=True, blank=True)
    production_page = models.CharField(max_length=255, null=True, blank=True)

    doc_image1 = models.ImageField(upload_to="images/", null=True, blank=True)
    doc_image2 = models.ImageField(upload_to="images/", null=True, blank=True)
    doc_image3 = models.ImageField(upload_to="images/", null=True, blank=True)
    doc_image4 = models.ImageField(upload_to="images/", null=True, blank=True)
    doc_image5 = models.ImageField(upload_to="images/", null=True, blank=True)


    #for bar owners
    business_permit = models.ImageField(upload_to="images/",null=True, blank=True)

    #for individual // all
    government_id = models.ImageField(upload_to="images/", null=True, blank=True)
    government_id_type = models.CharField(max_length=255, null=True, blank=True)

    @property
    def is_artist(self):
        return self.role == 'artist'

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.title()

    class Meta:
        ordering = ['first_name','last_name']


class Profile(models.Model):
    profile_image = models.ImageField(upload_to="images/profiles/", null=True, blank=True)
    dob = models.DateField(blank=True, null=True, validators=[date_not_future])
    gender = models.CharField(max_length=20, null=True, blank=True)
    # Contacts
    phone = models.CharField(max_length=20, blank=True, null=True)
    # Address
    country = models.CharField(max_length=255, default="philippines", null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    municipality = models.CharField(max_length=255, null=True, blank=True)
    brgy = models.CharField(max_length=60, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    is_complete = models.BooleanField(default=False)

    # Socials
    fb_page = models.CharField(max_length=255, null=True, blank=True)
    # Relationships
    user = models.OneToOneField(
        UserAccount, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    #new fields
    nationality = models.CharField(max_length=50, default="filipino")
    language = models.CharField(max_length=255, null=True, blank=True)





    def __str__(self):
        return f'P-{self.user}'

    class Meta:
        ordering = ['user']


class BusinessBoost(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='business_boost')

    page_name = models.CharField(max_length=255)
    page_id = models.CharField(max_length=255, null=True, blank=True)  # Store Facebook Page ID
    access_token = models.TextField()  # Store access token securely

    is_active = models.BooleanField(default=False)  # To track if Business Boost is enabled
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_access_token(self, token):
        # Encrypt the token before saving
        fernet = Fernet(settings.ENCRYPTION_KEY)
        self.access_token = fernet.encrypt(token.encode()).decode()

    def get_access_token(self):
        # Decrypt the token when retrieving
        fernet = Fernet(settings.ENCRYPTION_KEY)
        return fernet.decrypt(self.access_token.encode()).decode()
