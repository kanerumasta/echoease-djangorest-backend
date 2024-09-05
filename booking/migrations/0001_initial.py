# Generated by Django 5.0.7 on 2024-09-05 00:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artists', '0028_artist_award_image1_artist_award_image2_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=100)),
                ('event_date', models.DateField()),
                ('event_time', models.TimeField()),
                ('duration_in_hours', models.IntegerField(blank=True, null=True)),
                ('duration_in_minutes', models.IntegerField(blank=True, null=True)),
                ('event_location', models.CharField(max_length=255)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('cancelled', 'Cancelled'), ('approved', 'Approved'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='artists.artist')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]