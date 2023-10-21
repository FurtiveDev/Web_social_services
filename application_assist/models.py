from django.db import models


class RequestServices(models.Model):
    id_request_services = models.AutoField(primary_key=True)
    id_request = models.ForeignKey('Requests', models.DO_NOTHING, db_column='id_request', blank=True, null=True)
    id_service = models.ForeignKey('Services', models.DO_NOTHING, db_column='id_service', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'request_services'


class Requests(models.Model):
    id_request = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    formation_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    creator = models.IntegerField(blank=True, null=True)
    moderator = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'requests'


class Services(models.Model):
    id_service = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    location_service = models.CharField(max_length=255, blank=True, null=True)
    support_hours = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'services'


class Users(models.Model):
    id_user = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'users'
