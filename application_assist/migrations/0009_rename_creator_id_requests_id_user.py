# Generated by Django 4.2.6 on 2023-10-29 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application_assist', '0008_alter_requests_creator_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requests',
            old_name='creator_id',
            new_name='id_user',
        ),
    ]
