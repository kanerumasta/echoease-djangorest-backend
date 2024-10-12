# Generated by Django 5.0.7 on 2024-10-10 11:07

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
            name='ArtistDispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('under_review', 'Under Review'), ('resolved', 'Resolved'), ('escalated', 'Escalated')], default='under_review')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reason', models.CharField(choices=[('performance_quality', 'Performance Quality'), ('cancellation', 'Cancellation'), ('no_show', 'No Show'), ('miscommunication', 'Miscommunication'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('date_resolved', models.DateField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True, null=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='artists.artist')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artist_disputes', to='booking.booking')),
            ],
        ),
        migrations.CreateModel(
            name='ClientDispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('under_review', 'Under Review'), ('resolved', 'Resolved'), ('escalated', 'Escalated')], default='under_review', max_length=50)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(choices=[('performance_quality', 'Performance Quality'), ('cancellation', 'Cancellation'), ('no_show', 'No Show'), ('miscommunication', 'Miscommunication'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('date_resolved', models.DateField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True, null=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_disputes', to='booking.booking')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
