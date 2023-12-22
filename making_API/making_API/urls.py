from django.contrib import admin
from services import views
from django.urls import include, path
from rest_framework import routers
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),


    path(r'services/', views.services_list, name='service-list'),
    path(r'services/post/', views.services_list_create, name='service-list-create'),
    path(r'services/<int:id_service>/', views.get_service_detail, name='get-service-detail'),
    path(r'services/<int:id_service>/put/', views.update_service_detail, name='update-service-detail'),
    path(r'services/<int:id_service>/delete/', views.delete_service_detail, name='delete-service-detail'),


    path(r'requests/', views.requests_list, name='request-list'),
    path(r'requests/<int:id_request>/', views.get_request_detail, name='get-request-detail'),
    path(r'requests/<int:id_request>/put/', views.update_request_detail, name='update-request-detail'),
    path(r'requests/<int:id_request>/delete/', views.delete_request_detail, name='delete-request-detail'),
    path(r'requests/<int:id_request>/AdminPut/', views.putRequestByAdmin, name='request-put'),
    path(r'requests/UserPut/', views.putRequestByUser, name='request-put'),


    path(r'users/<int:id_user>/', views.user_detail, name='user-detail'),
    path(r'users/', views.all_users_detail, name='user-list'),

   
    path(r'services_requests/<int:id_service>/put/', views.PostRequestToService, name='user-put'),
    path(r'services/<int:id_service>/image/', views.postServiceImage, name='post_service_image'),

    
    path(r'login',  views.login_view, name='login'),
    path(r'logout', views.logout_view, name='logout'),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'admin/', admin.site.urls),
]