# Generated by Django 5.0.7 on 2024-09-01 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0024_rename_fb_page_artist_fb_link_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='artist',
            old_name='genre',
            new_name='genres',
        ),
    ]
