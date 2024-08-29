from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

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
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    profile_image = CloudinaryField(
        'profile_image', null=True, default=None, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    

    # Roles
    Roles = (('artist', 'Artist'), ('client', 'Client'), ('admin', 'Admin'))
    role = models.CharField(choices=Roles, default='client',
                            max_length=20, null=True, blank=True)

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
        return self.email


class ClientProfile(models.Model):

    dob = models.DateField(blank=True, null=True, validators=[date_not_future])
    gender = models.CharField(max_length=20, null=True, blank=True)

    # Contacts
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Address
    street = models.CharField(max_length=255, null=True, blank=True)
    brgy = models.CharField(max_length=60, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)  # or town
    country = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)

    # Photos
   

    # Socials
    fb_page = models.CharField(max_length=255, null=True, blank=True)

    # Relationships
    user = models.OneToOneField(
        UserAccount, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user}'

