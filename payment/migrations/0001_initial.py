# Generated by Django 5.0.7 on 2024-10-14 11:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artists', '0001_initial'),
        ('booking', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_reference', models.CharField(blank=True, max_length=15)),
                ('payment_status', models.CharField(default='pending', max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('platform_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_intent_id', models.CharField(max_length=255, unique=True)),
                ('service_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_gateway', models.CharField(blank=True, max_length=50, null=True)),
                ('payer_email', models.CharField(blank=True, max_length=50, null=True)),
                ('payer_name', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_type', models.CharField(choices=[('downpayment', 'Downpayment'), ('final_payment', 'Final Payment'), ('payout', 'Payout'), ('refund', 'Refund')], max_length=25)),
                ('artist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='artists.artist')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='booking.booking')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
