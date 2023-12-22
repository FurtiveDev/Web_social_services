from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from services.serializers import *
from .models import Requests
from .models import Services
from .models import CustomUser
# from .models import Users
from .models import RequestServices
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from minio import Minio
from minio.error import S3Error
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes
from django.conf import settings
import redis
import uuid
from django.contrib.sessions.models import Session
from services.permissions import *

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class CurrentUserSingleton: 
    _instance = None 
 
    @classmethod 
    def get_instance(cls): 
        if not cls._instance: 
            cls._instance = cls._get_user() 
        return cls._instance 
 
    @classmethod 
    def _get_user(cls): 
        return CustomUser.objects.get(email='test@mail.ru', password='pbkdf2_sha256$600000$PxEZbMzzP7Ixb2f8TULs5e$UB+lN2K7/gpblGhsncTxQx7v8t0vMR4awzHEiOfIB1c=')
    
#Услуги API
@api_view(['GET'])
def services_list(request):
    """
    Метод для вывода списка услуг и создание услуг
    """
    if request.method == 'POST':
        request.data['status'] = 'operating'
        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        services = Services.objects.filter(status='operating')
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsManager])
def services_list_create(request):
    """
    создание услуг
    """
    if request.method == 'POST':
        request.data['status'] = 'operating'
        serializer = ServicesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def get_service_detail(request, id_service):
    services = get_object_or_404(Services, id_service=id_service, status='operating')
    serializer = ServicesSerializer(services)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsManager])
def update_service_detail(request, id_service):
    services = get_object_or_404(Services, id_service=id_service, status='operating')
    serializer = ServicesSerializer(services, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_service_detail(request, id_service):
    services = get_object_or_404(Services, id_service=id_service, status='operating')
    services.status = 'deleted'
    services.save()
    return Response(f'Успешно удален', status=status.HTTP_204_NO_CONTENT)
    
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
@permission_classes([AllowAny])  # Adjust permissions as needed
def requests_list(request):
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

@api_view(['GET'])
def get_request_detail(request, id_request):
    request_item = get_object_or_404(Requests, id_request=id_request)
    serializer = RequestsSerializer(request_item)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuth])  # Adjust permissions as needed
def update_request_detail(request, id_request):
    request_item = get_object_or_404(Requests, id_request=id_request)
    serializer = RequestsSerializer(request_item, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager])  # Adjust permissions as needed
def delete_request_detail(request, id_request):
    try:
        request_item = Requests.objects.get(id_request=id_request)
    except Requests.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_item.status = 'deleted'
    request_item.save()
    return Response(f'Успешно удален', status=status.HTTP_204_NO_CONTENT)
    
@api_view(['PUT'])
@permission_classes([IsManager])
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
@permission_classes([IsAuth])
def putRequestByUser(request):
    request.data['status'] = 'registered' # Статус при создании по умолчанию == зарегестрирован
    # request.data['id_user'] = current_user.id_user # id_user при создании по умолчанию == id_user
    request.data['creation_date'] = datetime.now().date()
    serializer = RequestsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#Пользователи API
@api_view(['GET'])
def all_users_detail(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, id_user):
    try:
        user = CustomUser.objects.get(id_user=id_user)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
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
    try: 
        Requests_var = Requests.objects.filter(id_user=1, status="registered").latest('creation_date')
    except:
        Requests_var = Requests(
            status='registered',
            creation_date=datetime.now(),
            id_user=1,
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

# Authorization methods

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request):
        print('req is', request.data)
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     full_name=serializer.data['full_name'],
                                     phone_number=serializer.data['phone_number'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, serializer.data['email'])
            user_data = {
                "email": request.data['email'],
                #"full_name": request.data['full_name'],
                #"phone_number": request.data['phone_number'],
                "is_superuser": False
            }

            print('user data is ', user_data)
            response = Response(user_data, status=status.HTTP_201_CREATED)
            # response = HttpResponse("{'status': 'ok'}")
            response.set_cookie("session_id", random_key)
            return response
            # return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=username, password=password)
    if user is not None:
        print(user)
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)
        user_data = {
            "id_user": user.id_user,
            "email": user.email,
            #"full_name": user.full_name,
            #"phone_number": user.phone_number,
            "password": user.password,
            #"is_superuser": user.is_superuser,
        }
        response = Response(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", random_key, samesite="Lax", max_age=30 * 24 * 60 * 60)
        return response
    else:
        return HttpResponse("login failed", status=400)

@api_view(['POST'])
@permission_classes([IsAuth])
def logout_view(request):
    ssid = request.COOKIES["session_id"]
    if session_storage.exists(ssid):
        session_storage.delete(ssid)
        response_data = {'status': 'Success'}
    else:
        response_data = {'status': 'Error', 'message': 'Session does not exist'}
    return Response(response_data)

@api_view(['GET'])
# @permission_classes([IsAuth])
def user_info(request):
    try:
        ssid = request.COOKIES["session_id"]
        if session_storage.exists(ssid):
            email = session_storage.get(ssid).decode('utf-8')
            user = CustomUser.objects.get(email=email)
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "is_superuser": user.is_superuser
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Error', 'message': 'Session does not exist'})
    except:
        return Response({'status': 'Error', 'message': 'Cookies are not transmitted'})