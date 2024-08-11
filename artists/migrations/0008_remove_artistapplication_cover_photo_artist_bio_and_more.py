# Generated by Django 5.0.7 on 2024-08-11 05:28

import artists.validators
import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0007_alter_artistapplication_brgy_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artistapplication',
            name='cover_photo',
        ),
        migrations.AddField(
            model_name='artist',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='brgy',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='cover_photo',
            field=cloudinary.models.CloudinaryField(blank=True, default=None, max_length=255, null=True, verbose_name='cover_photo'),
        ),
        migrations.AddField(
            model_name='artist',
            name='dob',
            field=models.DateField(blank=True, null=True, validators=[artists.validators.date_not_future]),
        ),
        migrations.AddField(
            model_name='artist',
            name='fb_page',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='fb_profile_link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='gender',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='instagram',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(blank=True, default=None, max_length=255, null=True, verbose_name='profile_image'),
        ),
        migrations.AddField(
            model_name='artist',
            name='street',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='twitter',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='zipcode',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.DeleteModel(
            name='ArtistProfile',
        ),
    ]