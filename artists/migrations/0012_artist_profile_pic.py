# Generated by Django 5.0.7 on 2024-08-16 01:40

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0011_artistapplication_profile_pic_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='profile_pic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='artist_profile_pic'),
        ),
    ]