# Generated by Django 5.0.7 on 2024-11-01 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_useraccount_business_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='is_suspended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='reputation_score',
            field=models.IntegerField(default=100),
        ),
    ]
