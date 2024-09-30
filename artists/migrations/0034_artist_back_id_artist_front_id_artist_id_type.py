# Generated by Django 5.0.7 on 2024-09-17 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0033_alter_portfolioitem_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='back_id',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='artist',
            name='front_id',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='artist',
            name='id_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]