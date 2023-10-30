from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from services.serializers import ServicesSerializer
from services.serializers import RequestsSerializer
from services.serializers import RequestServicesSerializer
from .models import Requests
from .models import Services
from .models import Users
from .models import RequestServices
from rest_framework.views import APIView
from rest_framework.decorators import api_view

class CurrentUser: 
    _instance = None 
 
    @classmethod 
    def get_instance(cls): #Закомментировать если нужен модератор
        if not cls._instance: 
            cls._instance = cls._get_user() 
        return cls._instance
    # def get_instance(cls): 
    #     if not cls._instance: 
    #         cls._instance = cls._get_moderator()
    #     return cls._instance 
 
    @classmethod 
    def _get_user(cls): #Закомментировать если нужен модератор
        return Users.objects.get(id_user=1,first_name='User', password='1111', is_moderator=False)
    # def _get_moderator(cls):
    #     return Users.objects.get(id_user=2,first_name='Mod', password='1111' , is_moderator=True)
    
@api_view(['GET', 'POST'])
def services_list(request):
    """
    Метод для вывода списка услуг и создание услуг
    """
    current_user = CurrentUser.get_instance()
    if request.method == 'GET' and not current_user.is_moderator:
        services = Services.objects.filter(status = 'operating')
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data)

    elif request.method == 'POST' and current_user.is_moderator:
        request.data['status'] = 'operating' # Статус при создании по умолчанию == operating
        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #Модератор видит все записи, даже удаленные
    elif request.method == 'GET' and current_user.is_moderator:
        services = Services.objects.all()
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def services_detail(request, id_service):
    current_user = CurrentUser.get_instance()
    if Services.objects.filter(id_service=id_service, status='operating').exists():
        services = get_object_or_404(Services, id_service=id_service)
        if request.method == 'GET':
            serializer = ServicesSerializer(services)
            return Response(serializer.data)
        
        elif request.method == 'PUT' and current_user.is_moderator:
            serializer = ServicesSerializer(services,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE' and current_user.is_moderator:
            serializer = ServicesSerializer(services)
            services.status = 'deleted'
            return Response(f'Успешно удален',status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(f"Такой услуги не существует", status=status.HTTP_404_NOT_FOUND)
    



#Requests API
@api_view(['GET', 'POST'])
def requests_list(request):
    current_user = CurrentUser.get_instance()
    if request.method == 'GET' and not current_user.is_moderator: #Пользователь просматривает записи только для него
        Requests_var = Requests.objects.filter(id_user=current_user.id_user)
        serializer = RequestsSerializer(Requests_var, many=True)
        return Response(serializer.data)

    elif request.method == 'POST' and not current_user.is_moderator:
        request.data['status'] = 'registered' # Статус при создании по умолчанию == зарегестрирован
        request.data['id_user'] = current_user.id_user # id_user при создании по умолчанию == id_user
        serializer = RequestsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET' and current_user.is_moderator: # Просмотр заявок модератором
        Requests_var = Requests.objects.all()
        serializer = RequestsSerializer(Requests_var, many=True)
        return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def requests_detail(request, id_request):
    current_user = CurrentUser.get_instance()
    #Пользователь
    if Requests.objects.filter(id_request=id_request).exists() and not current_user.is_moderator:
        Requests_var = get_object_or_404(Requests, id_request=id_request,id_user=current_user.id_user)
        if request.method == 'GET':
            serializer = RequestsSerializer(Requests_var)
            return Response(serializer.data)
    
        elif request.method == 'PUT':
                request.data['id_request'] = id_request # пользователь не может менять id на любой который вздумается
                serializer = RequestServicesSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            serializer = RequestsSerializer(Requests_var)
            return Response(f'Успешно удален',status=status.HTTP_204_NO_CONTENT)
    #Модератор
    elif Requests.objects.filter(id_request=id_request).exists() and current_user.is_moderator:
        Requests_var = get_object_or_404(Requests, id_request=id_request)
        if request.method == 'GET':
            request.data['status'] = 'moderating' # Статус при просмотре по умолчанию == на рассмотрении
            serializer = RequestsSerializer(Requests_var)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = RequestsSerializer(Requests_var,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            serializer = RequestsSerializer(Requests_var)
            return Response(f'Успешно удален',status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(f"Такой услуги не существует", status=status.HTTP_404_NOT_FOUND)
