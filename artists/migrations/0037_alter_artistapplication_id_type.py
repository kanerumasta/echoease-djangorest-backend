# Generated by Django 5.0.7 on 2024-09-17 14:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0036_idtype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistapplication',
            name='id_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='artists.idtype'),
        ),
    ]
