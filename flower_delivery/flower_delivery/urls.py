from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('flowers.urls')),
    path('', RedirectView.as_view(url='/catalog/', permanent=True)),
]