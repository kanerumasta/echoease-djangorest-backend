# Generated by Django 5.0.7 on 2024-10-21 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0004_artist_business_boost_opted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='business_boost_opted',
        ),
        migrations.DeleteModel(
            name='BusinessBoost',
        ),
    ]
