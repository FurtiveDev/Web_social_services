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
import requests
from django.contrib.sessions.models import Session
from services.permissions import *
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

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
    title = request.query_params.get("title")

    services = Services.objects.filter(status="operating")

    if title:
        services = services.filter(service_name__icontains=title)
    try:
        ssid = request.COOKIES["session_id"]
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
        req = Requests.objects.filter(id_user=current_user, status="зарегистрирован").latest('creation_date')
        serializer = ServicesSerializer(services, many=True)
        req_serializer = RequestsSerializer(req)
        result = {
            'id_request': req_serializer.data['id_request'],
            'services': serializer.data
        }
        return Response(result)
    except:
        serializer = ServicesSerializer(services, many=True)
        result = {
            'services': serializer.data
        }
        return Response(result)


@api_view(['POST'])
@permission_classes([IsManager])
def services_list_create(request):
    data = request.data.copy()  # Создаем копию данных запроса
    data["status"] = "operating" 

    serializer = ServicesSerializer(data=data)
    if serializer.is_valid():
        new_option = serializer.save()
        # Removed image upload logic
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_service_detail(request, id_service):
    services = get_object_or_404(Services, id_service=id_service, status='operating')
    serializer = ServicesSerializer(services)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsManager])
def update_service_detail(request, pk):
    if not Services.objects.filter(pk=pk).exists():
        return Response(f"Услуги с таким id нет", status=status.HTTP_404_NOT_FOUND)
    serv = get_object_or_404(Services, pk=pk)
    serializer = ServicesSerializer(serv, data=request.data)
    if serializer.is_valid():
        serializer.save()
        print(ServicesSerializer(serv, data=request.data))
        return Response(serializer.data)
    print('Validation errors:', serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_service_detail(request, pk):
    if not Services.objects.filter(pk=pk).exists():
        return Response(f"Услуги с таким id нет")
    serv = Services.objects.get(pk=pk)
    serv.status = "deleted"
    serv.save()

    serv = Services.objects.filter(status="operating")
    serializer = ServicesSerializer(serv, many=True)
    return Response(serializer.data)
    
#Картинка
@api_view(['POST'])
@permission_classes([IsManager])
def postServiceImage(request, pk):
    if 'file' in request.FILES:
        file = request.FILES['file']
        serv = Services.objects.get(pk=pk, status='operating')
        client = Minio(endpoint="localhost:9000",
                       access_key='minioadmin',
                       secret_key='minioadmin',
                       secure=False)

        bucket_name = 'images'
        file_name = file.name
        file_path = "http://localhost:9000/images/" + file_name
        
        try:
            client.put_object(bucket_name, file_name, file, length=file.size, content_type=file.content_type)
            print("Файл успешно загружен в Minio.")
            
            serializer = ServicesSerializer(instance=serv, data={'image': file_path}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse('Image uploaded successfully.')
            else:
                return HttpResponseBadRequest('Invalid data.')
        except Exception as e:
            print("Ошибка при загрузке файла в Minio:", str(e))
            return HttpResponseServerError('An error occurred during file upload.')

    return HttpResponseBadRequest('Invalid request.')

#Запросы API
@api_view(['GET'])
@permission_classes([IsAuth])  # Adjust permissions as needed
def requests_list(request):
   try:
       if "session_id" in request.COOKIES:
          ssid = request.COOKIES["session_id"]
       else: 
          return HttpResponseForbidden('Сессия не найдена')
       
       email = session_storage.get(ssid).decode('utf-8')
       current_user = CustomUser.objects.get(email=email)
       date_format = "%Y-%m-%d"
       start_date_str = request.query_params.get('start', '2020-01-01')
       end_date_str = request.query_params.get('end', '2025-12-31')
       start = datetime.strptime(start_date_str, date_format).date()
       end = datetime.strptime(end_date_str, date_format).date()
       
       status = request.query_params.get('status')
       email_filter = request.query_params.get('email', None)

       if current_user.is_superuser: # Модератор может смотреть заявки всех пользователей
           reqs = Requests.objects.filter(
               ~Q(status="удален"),
               creation_date__range=(start, end)
           )
       else: # Авторизованный пользователь может смотреть только свои заявки
            reqs = Requests.objects.filter(
                ~Q(status="удален"),
                id_user=current_user.id_user,
                creation_date__range=(start, end)
            )
       
       if email_filter:
           
           reqs = reqs.filter(Q(user__icontains=email_filter))

       if status:
           reqs = reqs.filter(status=status)

       serializer = RequestsSerializer(reqs, many=True)
       
       return Response(serializer.data)
   except:
       return HttpResponseForbidden('Сессия не найдена')

"""@api_view(['GET'])
@permission_classes([IsAuth])
def get_request_detail(request,pk):
  ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response('Сессия не найдена')
    
    try:
        req = Services.objects.get(pk=pk)
        if req.status == "deleted" or not req:
            return Response("Заявки с таким id нет")
        req_serializer = RequestsSerializer(req)
        if (not current_user.is_superuser and current_user.id == req_serializer.data['id_user']) or (current_user.is_superuser):
            req_ser = RequestServices.objects.filter(id_request=req)
            subscription_ids = [subscription.id_subscription_id for subscription in application_subscriptions]
            print(subscription_ids)
            subscriptions_queryset = Subscription.objects.filter(id__in=subscription_ids)
            subscriptions_serializer = SubscriptionSerializer(subscriptions_queryset, many=True)
            response_data = {
                'application': application_serializer.data,
                'subscriptions': subscriptions_serializer.data
            }
            return Response(response_data)
        else: 
            return Response("Заявки с таким id нет")
    except Application.DoesNotExist:
        return Response("Заявки с таким id нет")"""
@api_view(['PUT'])
@permission_classes([IsAuth])
def request_send(request):
    ssid = request.COOKIES.get("session_id")
    if not ssid:
        return Response('Сессия не найдена')
    
    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response('Пользователь не найден')
    except KeyError:
        return Response('Сессия не найдена')

    try:
        req = get_object_or_404(Requests, id_user=current_user, status="зарегистрирован")
    except:
        return Response("Такой заявки не зарегистрировано")
    
    req.status = "на рассмотрении"
    req.creation_date = datetime.now()# Исправить тут!
    print(req.creation_date)
    req.save()

    # Send the request id to the external service
    external_service_url = "http://localhost:8080/asyncProcess"
    payload = {"id_request": req.id_request}
    try:
        external_response = requests.post(external_service_url, json=payload)
        external_response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        # Handle any errors that occur during the request
        return Response(f"Ошибка при обращении к внешнему сервису: {str(e)}")

    # If the external service call was successful, include its response
    serializer = RequestsSerializer(req)
    data = serializer.data
    data['external_service_response'] = external_response.json()
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuth])
def get_request_detail(request,pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response('Сессия не найдена')
    
    try:
        req = Requests.objects.get(pk=pk)
        if req.status == "удален" or not req:
            return Response("Заявки с таким id нет")
        request_serializer = RequestsSerializer(req)
        if (not current_user.is_superuser and current_user.id_user == request_serializer.data['id_user']) or (current_user.is_superuser):
            req_serv = RequestServices.objects.filter(id_request=req)
            services_ids = [services.id_service_id for services in req_serv]
            print(services_ids)
            services_queryset = Services.objects.filter(id_service__in=services_ids)
            services_serializer = ServicesSerializer(services_queryset, many=True)
            response_data = {
                'request': request_serializer.data,
                'services': services_serializer.data
            }
            return Response(response_data)
        else: 
            return Response("Заявки с таким id нет")
    except Requests.DoesNotExist:
        return Response("Заявки с таким id нет")
    
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
@permission_classes([IsAuth])
def delete_request_detail(request):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response('Сессия не найдена')
    try: 
        application = Requests.objects.get(id_user=current_user, status="зарегистрирован")
        application.status = "удален"
        application.save()
        return Response({'status': 'Success'})
    except:
        return Response("У данного пользователя нет заявки", status=400)
    
@api_view(['PUT'])
@permission_classes([IsManager])
def putRequestByAdmin(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response('Сессия не найдена')

    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id нет")
    req = Requests.objects.get(pk=pk)
    if req.status != "на рассмотрении":
        return Response("Такой заявки нет на проверке")
    if request.data["status"] not in ["отказано", "принято"]:
        return Response("Неверный статус!")
    req.status = request.data["status"]
    req.completion_date=datetime.now()
    req.id_moderator = current_user
    req.save()
    serializer = RequestsSerializer(req)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuth])
def putRequestByUser(request):
    request.data['status'] = 'зарегистрирован' # Статус при создании по умолчанию == зарегестрирован
    # request.data['id_user'] = current_user.id_user # id_user при создании по умолчанию == id_user
    request.data['creation_date'] = datetime.now()
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

#Услуги добавление APIX
@api_view(['DELETE'])
@permission_classes([IsAuth])
def DeleteRequestToService(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response('Сессия не найдена')
    request = get_object_or_404(Requests, id_user=current_user, status="зарегистрирован")
    try:
        service = Services.objects.get(pk=pk, status='operating')
        subscriptionsFromApplication = RequestServices.objects.filter(id_request = request)
        try:
            request_service = get_object_or_404(RequestServices, id_service=service, id_request=request)
            request_service.delete()
            if (len(subscriptionsFromApplication) == 0):
                request = get_object_or_404(Requests, id_user=current_user, status="зарегистрирован")
                request.status = 'удален'
                request.save()
            return Response("Услуга удалена", status=200)
        except RequestServices.DoesNotExist:
            return Response("Заявка не найдена", status=404)
    except Services.DoesNotExist:
        return Response("Такой услуги нет", status=400)
    

@api_view(['POST'])
@permission_classes([IsAuth])
def PostRequestToService(request, pk):
    ssid = request.COOKIES.get("session_id")
    if not ssid:
        return Response('Сессия не найдена', status=400)

    try:
        email = session_storage.get(ssid).decode('utf-8')
        current_user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response('Пользователь не найден', status=404)

    try:
        current_request = Requests.objects.filter(id_user=current_user, status="зарегистрирован").latest('creation_date')
    except Requests.DoesNotExist:
        current_request = Requests(
            status='зарегистрирован',
            creation_date=datetime.now(),
            id_user=current_user,
        )
        current_request.save()

    try:
        service = Services.objects.get(pk=pk, status='operating')
    except Services.DoesNotExist:
        return Response("Такой услуги нет", status=404)

    try:
        request_service = RequestServices.objects.get(id_request=current_request, id_service=service)
        return Response("Услуга уже добавлена в запрос", status=400)
    except RequestServices.DoesNotExist:
        request_service = RequestServices(
            id_request=current_request,
            id_service=service,
        )
        request_service.save()

    added_service = Services.objects.get(pk=pk)
    serializer = ServicesSerializer(added_service)
    # Add the id_request to the response data
    response_data = serializer.data
    response_data['id_request'] = current_request.id_request
    return Response(response_data, status=201)

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
                "full_name": request.data['full_name'],
                "phone_number": request.data['phone_number'],
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
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "password": user.password,
            "is_superuser": user.is_superuser,
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
                "id_user": user.id_user,
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