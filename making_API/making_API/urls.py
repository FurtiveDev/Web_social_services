from django.contrib import admin
from services import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'services/', views.services_list, name='service-list'),
    path(r'services/<int:id_service>/', views.services_detail, name='service-detail'),
    path(r'requests/', views.requests_list, name='request-list'),
    path(r'requests/<int:id_request>/', views.requests_detail, name='request-detail'),
    path(r'requests/<int:id_request>/AdminPut/', views.putRequestByAdmin, name='request-put'),
    path(r'requests/UserPut/', views.putRequestByUser, name='request-put'),
    path(r'users/<int:id_user>/', views.user_detail, name='user-detail'),
    path(r'users/', views.all_users_detail, name='user-list'),
    path(r'services_requests/<int:id_service>/put/', views.PostRequestToService, name='user-put'),
    path(r'services/<int:id_service>/image/', views.postServiceImage, name='post_service_image'),
    path(r'update-request-status/<int:id_request>/', views.UpdateRequestStatusView, name='update-request-status'),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'admin/', admin.site.urls),
]