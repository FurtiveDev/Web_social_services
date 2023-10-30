from django.contrib import admin
from services import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'services/', views.services_list, name='service-list'),
    path(r'services/<int:id_service>/', views.services_detail, name='service-detail'),
    # path(r'services/<int:id_service>/put/', views.put_detail, name='service-put'),
    path(r'requests/', views.requests_list, name='request-list'),
    path(r'requests/<int:id_request>/', views.requests_detail, name='request-detail'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]