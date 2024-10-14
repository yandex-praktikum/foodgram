from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.services import redirection

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('<str:short_url>/', redirection),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
