# Generated by Django 5.0.7 on 2024-09-17 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0035_remove_artist_back_id_remove_artist_front_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='IDType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
