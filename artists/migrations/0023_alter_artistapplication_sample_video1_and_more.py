# Generated by Django 5.0.7 on 2024-08-31 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0022_rename_genre_artistapplication_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistapplication',
            name='sample_video1',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AlterField(
            model_name='artistapplication',
            name='sample_video2',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AlterField(
            model_name='artistapplication',
            name='sample_video3',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
    ]
