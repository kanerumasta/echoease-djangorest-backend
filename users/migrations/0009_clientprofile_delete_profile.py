# Generated by Django 5.0.7 on 2024-08-08 01:22

import cloudinary.models
import django.db.models.deletion
import users.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_rename_postal_code_profile_zipcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField(blank=True, null=True, validators=[users.validators.date_not_future])),
                ('gender', models.CharField(blank=True, max_length=20, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('street', models.CharField(blank=True, max_length=255, null=True)),
                ('brgy', models.CharField(blank=True, max_length=60, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
                ('profile_image', cloudinary.models.CloudinaryField(blank=True, default=None, max_length=255, null=True, verbose_name='profile_image')),
                ('fb_page', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]