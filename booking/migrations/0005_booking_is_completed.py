# Generated by Django 5.0.7 on 2024-09-19 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_alter_booking_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
