# Generated by Django 5.0.7 on 2024-09-22 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0041_rate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artistapplication',
            name='rate',
        ),
    ]