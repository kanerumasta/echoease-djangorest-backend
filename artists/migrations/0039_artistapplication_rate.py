# Generated by Django 5.0.7 on 2024-09-19 17:32

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0038_artist_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistapplication',
            name='rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
