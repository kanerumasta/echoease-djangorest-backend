# Generated by Django 5.0.7 on 2024-10-08 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0052_alter_portfolioitem_portfolio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]