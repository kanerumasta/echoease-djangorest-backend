# Generated by Django 5.0.7 on 2024-07-15 08:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_useraccount_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.profile'),
        ),
    ]
