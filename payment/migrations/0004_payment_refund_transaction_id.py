# Generated by Django 5.0.7 on 2024-10-19 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_payment_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='refund_transaction_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
