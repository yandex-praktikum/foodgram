from django.contrib import admin
from rest_framework.routers import DefaultRouter
from users.views import UsersViewSet
from django.urls import path, include


router_vers1 = DefaultRouter()
router_vers1.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router_vers1.urls)),
#    path('auth/', include('djoser.urls')),
#    path('auth/', include('djoser.urls.jwt')),
]
