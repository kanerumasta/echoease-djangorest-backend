# Generated by Django 5.0.7 on 2024-08-29 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_useraccount_last_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ClientProfile',
            new_name='Profile',
        ),
    ]