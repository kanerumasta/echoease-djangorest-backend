# Generated by Django 5.0.7 on 2024-11-13 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_alter_booking_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='amount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
