# Generated by Django 5.0.7 on 2024-10-22 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_useraccount_business_boost_opted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='business_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]