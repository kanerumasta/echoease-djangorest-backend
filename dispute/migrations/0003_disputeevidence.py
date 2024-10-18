# Generated by Django 5.0.7 on 2024-10-17 12:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispute', '0002_dispute'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisputeEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to='dispute_evidences/')),
                ('dispute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidences', to='dispute.dispute')),
            ],
        ),
    ]