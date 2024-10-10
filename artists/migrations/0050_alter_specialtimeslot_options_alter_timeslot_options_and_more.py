# Generated by Django 5.0.7 on 2024-10-06 15:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0049_specialtimeslot'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='specialtimeslot',
            options={'ordering': ['start_time']},
        ),
        migrations.AlterModelOptions(
            name='timeslot',
            options={'ordering': ['start_time']},
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='image1',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='image2',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='image3',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='image4',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='image5',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='video1',
        ),
        migrations.RemoveField(
            model_name='portfolioitem',
            name='video2',
        ),
        migrations.CreateModel(
            name='PortfolioItemMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('video', 'Video'), ('image', 'Image')], max_length=50)),
                ('file', models.FileField(upload_to='media/')),
                ('portfolio_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medias', to='artists.portfolioitem')),
            ],
        ),
    ]
