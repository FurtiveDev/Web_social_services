# Generated by Django 4.2.6 on 2023-12-19 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_alter_requests_status_alter_services_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='requests',
            name='service_provided',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
