# Generated by Django 5.0.7 on 2024-09-01 16:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_useraccount_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='created',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraccount',
            name='modified',
            field=models.DateField(auto_now=True),
        ),
    ]
