from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from services.serializers import *
from .models import Requests
from .models import Services
from .models import Users
from .models import RequestServices
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

SECRET_KEY = 'aB3dE4gH'
@csrf_exempt
@require_http_methods(["PUT"])
def UpdateRequestStatusView(request, id_request):
    # Проверка ключа авторизации
    data = json.loads(request.body)
    print(data)
    secret_key = data.get('secretKey')
    if secret_key != SECRET_KEY:
        return JsonResponse({'message': 'Неавторизованный запрос'}, status=401)

    try:
        result = data['result']
        # Обновление статуса заявки
        application = Requests.objects.get(id_request=id_request)
        application.service_provided = result
        application.save()
        return JsonResponse({'message': 'Статус заявки обновлён'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'message': 'Неверный формат данных'}, status=400)
    except Requests.DoesNotExist:
        return JsonResponse({'message': 'Заявка не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

    
class CurrentUser: 
    _instance = None 
 
    @classmethod 
    def get_instance(cls):
        if not cls._instance: 
            cls._instance = cls._get_user() 
        return cls._instance

 
    @classmethod 
    def _get_user(cls):
        return Users.objects.get(id_user=1,first_name='User', password='1111', is_moderator=False)

#Услуги API
@api_view(['GET', 'POST'])
def services_list(request):
    """
    Метод для вывода списка услуг и создание услуг
    """
    current_user = CurrentUser.get_instance()
    if request.method == 'POST':
        request.data['status'] = 'operating'
        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        title = request.query_params.get('title')
        services_query = Services.objects.filter(status='operating')
        if title:
            services_query = services_query.filter(service_name__icontains=title)
        serializer = ServicesSerializer(services_query, many=True)
        return Response(serializer.data)
    
    
@api_view(['GET', 'PUT', 'DELETE'])
def services_detail(request, id_service):
    current_user = CurrentUser.get_instance()
    if Services.objects.filter(id_service=id_service, status='operating').exists():
        services = get_object_or_404(Services, id_service=id_service)
        if request.method == 'GET':
            serializer = ServicesSerializer(services)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = ServicesSerializer(services,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            serializer = ServicesSerializer(services)
            services.status = 'deleted'
            return Response(f'Успешно удален',status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(f"Такой услуги не существует", status=status.HTTP_404_NOT_FOUND)
    
#Картинка
@api_view(['POST'])
def postServiceImage(request, id_service):
    if Services.objects.filter(id_service=id_service, status='operating').exists():
        services = get_object_or_404(Services, id_service=id_service)
        serializer = ServicesSerializer(services, data=request.data)
        if not serializer.is_valid(): 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        new_option = serializer.save() 
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        client = Minio(endpoint="localhost:9000",
                access_key='minioadmin',
                secret_key='minioadmin',
                secure=False)
        i=new_option.id_service
        print(i)
        try:
            i = new_option.id_service
            img_obj_name = f"{i}.png"
            file_path = f"/home/dev/app_images/{request.data.get('image')}"  
            client.fput_object(bucket_name='images',
                            object_name=img_obj_name,
                            file_path=file_path)
            new_option.image = f"http://localhost:9000/images/{img_obj_name}"
            new_option.save()
        except Exception as e:
            return Response({"error": str(e)})
        
        
        option = Services.objects.filter(id_service=id_service)
        serializer = ServicesSerializer(option, many=True)
        return Response(serializer.data)
    else:
        return Response(f"Такой услуги не существует", status=status.HTTP_404_NOT_FOUND)

#Запросы API
@api_view(['GET'])
def requests_list(request):
    current_user = CurrentUser.get_instance()
    if request.method == 'GET':
        date_format = "%Y-%m-%d"
        start_date_str = request.query_params.get('start', '2020-01-01')
        end_date_str = request.query_params.get('end', '2023-12-31')
        start = datetime.strptime(start_date_str, date_format).date()
        end = datetime.strptime(end_date_str, date_format).date()
        status = request.query_params.get('status', None)
        Requests_var = Requests.objects.filter(creation_date__range=(start, end))
        if status:
            Requests_var = Requests_var.filter(status=status)
        Requests_var = Requests_var.order_by('creation_date')
        serializer = RequestsSerializer(Requests_var, many=True)
        return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def requests_detail(request, id_request):
    current_user = CurrentUser.get_instance()
    if Requests.objects.filter(id_request=id_request).exists():
        Requests_var = get_object_or_404(Requests, id_request=id_request)
        if request.method == 'GET':
            serializer = RequestsSerializer(Requests_var)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = RequestsSerializer(Requests_var,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            try:
                request_item = Requests.objects.get(id_request=id_request)
            except Requests.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            # Update the status to 'deleted'
            request_item.status = 'deleted'
            request_item.save()

            # Return a success response
            return Response(f'Успешно удален', status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(f"Такой услуги не существует", status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
def putRequestByAdmin(request, id_request):
    if not Requests.objects.filter(id_request=id_request).exists():
        return Response(f"Заявки с таким id нет")
    Requests_var = Requests.objects.get(id_request=id_request)
    if Requests_var.status != "moderating":
        return Response("Такой заявки нет на проверке")
    if request.data["status"] not in ["denied", "approved"]:
        return Response("Неверный статус!")
    Requests_var.status = request.data["status"]
    Requests_var.completion_date=datetime.now().date()
    Requests_var.save()
    serializer = RequestsSerializer(Requests_var)
    return Response(serializer.data)

@api_view(['PUT'])
def putRequestByUser(request):
    current_user = CurrentUser.get_instance()
    request.data['status'] = 'registered' # Статус при создании по умолчанию == зарегестрирован
    request.data['id_user'] = current_user.id_user # id_user при создании по умолчанию == id_user
    request.data['creation_date'] = datetime.now().date()
    serializer = RequestsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#Пользователи API
@api_view(['GET'])
def all_users_detail(request):
    users = Users.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, id_user):
    try:
        user = Users.objects.get(id_user=id_user)
    except Users.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UsersSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#Услуги добавление API
@api_view(['POST'])
def PostRequestToService(request, id_service):
    current_user = CurrentUser.get_instance()
    try: 
        Requests_var = Requests.objects.filter(id_user=current_user, status="registered").latest('creation_date')
    except:
        Requests_var = Requests(
            status='registered',
            creation_date=datetime.now(),
            id_user=current_user,
        )
        Requests_var.save()
    id_request = Requests_var
    try:
        Services_var = Services.objects.get(id_service=id_service, status='operating')
    except Services_var.DoesNotExist:
        return Response("Такой услуги нет", status=400)
    try:
        request_service_var = RequestServices.objects.get(id_request=id_request, id_service=Services_var)
        return Response("Такая услуга уже добавлена в заявку")
    except RequestServices.DoesNotExist:
        request_service_var = RequestServices(
            id_request=id_request,
            id_service=Services_var,
        )
        request_service_var.save()
    request_service_var = RequestServices.objects.filter(id_request = id_request)
    serializer = RequestServicesSerializer(request_service_var, many=True)
    return Response(serializer.data)