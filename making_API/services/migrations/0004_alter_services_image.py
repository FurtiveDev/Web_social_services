# Generated by Django 4.2.6 on 2023-10-30 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_remove_requests_been_moderated_alter_requests_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='services',
            name='image',
            field=models.BinaryField(blank=True, max_length=255, null=True),
        ),
    ]
