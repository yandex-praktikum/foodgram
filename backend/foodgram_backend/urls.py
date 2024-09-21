from django.contrib import admin
from django.urls import include, path

import recipes.urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(recipes.urls.urlpatterns)),
]
