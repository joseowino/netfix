from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from . import settings
from users.views import ProfileView

admin.site.site_header = 'My Site Administration'
admin.site.site_title = 'My Site Admin'

urlpatterns = [
    path('admin/', admin.site.urls),

    # App URLS
    path('', include('main.urls')),
    path('', include('users.urls')),
    path('services/', include('services.urls')),
    path('profile/<str:username>/', ProfileView, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)