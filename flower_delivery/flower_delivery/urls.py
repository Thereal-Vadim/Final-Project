from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Маршруты для login/logout
    path('', include('flowers.urls')),
    path('', RedirectView.as_view(url='/catalog/', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)