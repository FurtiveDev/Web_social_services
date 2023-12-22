# Generated by Django 4.2.6 on 2023-12-10 20:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import services.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id_service', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email адрес')),
                ('password', models.CharField(max_length=150, verbose_name='Пароль')),
                ('full_name', models.CharField(default='', max_length=50, verbose_name='ФИО')),
                ('phone_number', models.CharField(default='', max_length=30, verbose_name='Номер телефона')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Является ли пользователь менеджером?')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='Является ли пользователь админом?')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'managed': True,
            },
            managers=[
                ('objects', services.models.NewUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id_request', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(blank=True, choices=[('registered', 'зарегистрирован'), ('moderating', 'на рассмотрении'), ('approved', 'принято'), ('denied', 'отказано'), ('deleted', 'удален')], max_length=20, null=True)),
                ('creation_date', models.DateField(blank=True, null=True)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('id_user', models.ForeignKey(blank=True, db_column='id_user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'requests',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id_service', models.AutoField(primary_key=True, serialize=False)),
                ('service_name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=255, null=True)),
                ('location_service', models.CharField(blank=True, max_length=255, null=True)),
                ('support_hours', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, choices=[('operating', 'действует'), ('deleted', 'удален')], max_length=20, null=True)),
            ],
            options={
                'db_table': 'services',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RequestServices',
            fields=[
                ('id_request_services', models.AutoField(primary_key=True, serialize=False)),
                ('id_request', models.ForeignKey(blank=True, db_column='id_request', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='services.requests')),
                ('id_service', models.ForeignKey(blank=True, db_column='id_service', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='services.services')),
            ],
            options={
                'db_table': 'request_services',
                'managed': True,
            },
        ),
    ]
