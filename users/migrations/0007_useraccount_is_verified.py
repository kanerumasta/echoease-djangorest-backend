# Generated by Django 5.0.7 on 2024-07-16 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_useraccount_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]