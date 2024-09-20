# Generated by Django 5.0.7 on 2024-09-18 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0037_alter_artistapplication_id_type'),
        ('booking', '0003_alter_booking_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('artist', 'event_date')},
        ),
    ]
