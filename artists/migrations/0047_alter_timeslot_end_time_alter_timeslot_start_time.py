# Generated by Django 5.0.7 on 2024-10-05 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0046_timeslot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='end_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='start_time',
            field=models.TimeField(),
        ),
    ]