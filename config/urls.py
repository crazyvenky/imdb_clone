from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.titles.urls')),
    path('lists/', include('apps.lists.urls')),
    path('search/', include('apps.search.urls'))
]

# THIS IS THE MAGIC SAUCE FOR LOCAL IMAGES
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)