from services.models import *
from rest_framework import serializers
from services.models import CustomUser

class ServicesSerializer(serializers.ModelSerializer):
    #id_service = serializers.IntegerField(read_only=False)  #чтобы можно было добавлять с произвольным id
    class Meta:
        # Модель, которую мы сериализуем
        model = Services
        # Поля, которые мы сериализуем
        fields = ['id_service', 'service_name', 'description', 'image', 'location_service', 'support_hours', 'status']

class RequestsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Requests
        # Поля, которые мы сериализуем
        fields = ['id_request', 'status', 'creation_date', 'completion_date', 'id_user']

class RequestServicesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = RequestServices
        # Поля, которые мы сериализуем
        fields = ['id_request_services', 'id_request', 'id_service']

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'full_name', 'phone_number', 'is_staff', 'is_superuser']