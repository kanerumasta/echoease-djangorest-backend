# Generated by Django 5.0.7 on 2024-09-16 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0031_alter_portfolioitem_file_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolioitem',
            name='file',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='file_type',
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='group',
            field=models.CharField(blank=True, default='portfolio', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='image1',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='image4',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='image5',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
