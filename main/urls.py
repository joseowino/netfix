from django.urls import path, include
from django.conf.urls.static import static
from . import views as v
from django.contrib import admin
from django.conf import settings

app_name = "main"

urlpatterns = [
    path('', v.home, name='home'),
    path('logout/', v.logout, name='logout'),

    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('services/', include('services.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)