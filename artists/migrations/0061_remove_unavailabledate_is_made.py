# Generated by Django 5.0.7 on 2024-10-10 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0060_remove_defaulttimeslotexception_time_slot_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unavailabledate',
            name='is_made',
        ),
    ]
