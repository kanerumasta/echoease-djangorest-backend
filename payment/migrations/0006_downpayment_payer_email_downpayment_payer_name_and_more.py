# Generated by Django 5.0.7 on 2024-10-11 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_rename_payment_statys_downpayment_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='downpayment',
            name='payer_email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='downpayment',
            name='payer_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payer_email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payer_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
