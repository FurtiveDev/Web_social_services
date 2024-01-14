from django.db import models
from django.contrib.auth.models import PermissionsMixin , UserManager, AbstractBaseUser

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user
    class Meta:
        managed = True

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id_user = models.AutoField(primary_key=True)
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=150, verbose_name="Пароль") 
    full_name = models.CharField(max_length=50, default='', verbose_name='ФИО')
    phone_number = models.CharField(max_length=30, default='', verbose_name='Номер телефона')   
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    USERNAME_FIELD = 'email'

    objects =  NewUserManager()

    class Meta:
        managed = True
class RequestServices(models.Model):
    id_request_services = models.AutoField(primary_key=True)
    id_request = models.ForeignKey('Requests', models.DO_NOTHING, db_column='id_request', blank=True, null=True)
    id_service = models.ForeignKey('Services', models.DO_NOTHING, db_column='id_service', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'request_services'


class Requests(models.Model):
    STATUS_CHOICES = [
        ('registered', 'зарегистрирован'),
        ('moderating', 'на рассмотрении'),
        ('approved', 'принято'),
        ('denied', 'отказано'),
        ('deleted', 'удален')
    ]
    id_request = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS_CHOICES)
    creation_date = models.DateTimeField(blank=True, null=True) 
    completion_date =  models.DateTimeField(blank=True, null=True) 
    id_user = models.ForeignKey('CustomUser', models.DO_NOTHING, db_column='id_user', blank=True, null=True)
    service_provided = models.BooleanField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'requests'


class Services(models.Model):
    STATUS_CHOICES = [
        ('operating', 'действует'),
        ('deleted', 'удален')
    ]
    id_service = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    location_service = models.CharField(max_length=255, blank=True, null=True)
    support_hours = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS_CHOICES)

    class Meta:
        managed = True
        db_table = 'services'

