# Generated by Django 4.2.6 on 2023-10-21 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application_assist', '0004_rename_location_services_location_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='services',
            name='status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
