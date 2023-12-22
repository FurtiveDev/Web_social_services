from rest_framework import permissions
from .models import *
import redis
from django.conf import settings

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        # Проверка пользователя через объект request.user (обычно устанавливается middleware)
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True
        # Попытка использовать access_token из cookies для аутентификации
        access_token = request.COOKIES.get("session_id")
        # access_token = request.headers.get('Authorization')
        if access_token:
            try:
                username = session_storage.get(access_token).decode("utf-8")
                if username:
                    user = CustomUser.objects.filter(email=username).first()
                    if user and (user.is_superuser or user.is_staff):
                        return True
            except Exception as e:
                # Логирование или обработка исключения, если необходимо
                pass

        # Если ни один из методов аутентификации не удался
        return False

class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        # Проверка пользователя через объект request.user (обычно устанавливается middleware)
        if request.user and request.user.is_authenticated:
            return True

        # Попытка использовать access_token из cookies для аутентификации
        access_token = request.COOKIES.get("session_id")
        # access_token = request.headers.get('Authorization')
        if access_token:
            try:
                username = session_storage.get(access_token).decode("utf-8")
                if username:
                    # Убедитесь, что у вас есть соответствующий метод для поиска пользователя
                    user = CustomUser.objects.filter(email=username).first()
                    return bool(user)
            except Exception as e:
                # Логирование или обработка исключения, если необходимо
                pass

        # Если ни один из методов аутентификации не удался
        return False