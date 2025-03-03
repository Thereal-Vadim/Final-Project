from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# Создаём роутер для API
router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('catalog/', views.catalog, name='catalog'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_history/', views.order_history, name='order_history'),
    path('repeat_order/<int:order_id>/', views.repeat_order, name='repeat_order'),
    path('api/', include(router.urls)),  # Добавляем API маршруты
]