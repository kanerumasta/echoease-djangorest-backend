# Generated by Django 5.0.7 on 2024-10-12 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artists', '0002_remove_unavailabledate_is_made'),
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='artists.artist')),
            ],
        ),
        migrations.CreateModel(
            name='RecurringPattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_of_week', models.JSONField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_availabilities', to='artists.artist')),
            ],
        ),
    ]