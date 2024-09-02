# Generated by Django 5.0.7 on 2024-08-30 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_rename_clientprofile_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='city',
            new_name='municipality',
        ),
        migrations.AddField(
            model_name='profile',
            name='province',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]