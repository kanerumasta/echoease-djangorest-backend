# Generated by Django 5.0.7 on 2024-08-29 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0016_genre_artistapplication_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistapplication',
            name='genre',
            field=models.ManyToManyField(blank=True, to='artists.genre'),
        ),
    ]
