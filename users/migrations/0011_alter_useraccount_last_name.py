# Generated by Django 5.0.7 on 2024-08-29 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_clientprofile_profile_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]