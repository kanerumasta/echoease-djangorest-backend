# Generated by Django 5.0.7 on 2024-10-10 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0059_unavailabledate_is_made'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defaulttimeslotexception',
            name='time_slot',
        ),
        migrations.AlterUniqueTogether(
            name='defaulttimeslotexception',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='specialtimeslot',
            name='artist',
        ),
        migrations.DeleteModel(
            name='DefaultTimeSlot',
        ),
        migrations.DeleteModel(
            name='DefaultTimeSlotException',
        ),
        migrations.DeleteModel(
            name='SpecialTimeSlot',
        ),
    ]
