# Generated by Django 4.2.6 on 2023-10-21 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application_assist', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='services',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='services',
            name='support_hours',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
