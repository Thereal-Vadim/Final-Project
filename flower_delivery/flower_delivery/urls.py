from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Сохраняем аутентификацию
    path('', include('flowers.urls')),  # Основные маршруты приложения
    path('', RedirectView.as_view(url='/catalog/', permanent=True)),  # Перенаправление корня
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)