# Generated by Django 5.0.7 on 2024-08-01 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_rename_users_conversation_parcitipants'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conversation',
            old_name='parcitipants',
            new_name='participants',
        ),
    ]