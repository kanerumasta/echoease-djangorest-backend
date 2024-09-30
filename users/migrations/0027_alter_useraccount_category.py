# Generated by Django 5.0.7 on 2024-09-25 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_remove_useraccount_is_bar_owner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='category',
            field=models.CharField(choices=[('bar_owner', 'Bar Owner'), ('regular', 'Regular'), ('event_organizer', 'Event Organizer')], default='regular', max_length=50),
        ),
    ]
