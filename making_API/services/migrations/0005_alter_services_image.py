# Generated by Django 4.2.6 on 2023-10-30 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_alter_services_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='services',
            name='image',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]