from django.contrib import admin
from .models import Product, Order, OrderItem, Cart, CartItem, CustomUser, AdminTelegramUser

# Регистрация моделей
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_editable = ('status',)

@admin.register(AdminTelegramUser)
class AdminTelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_id')  # Отображение имени пользователя и chat_id
    search_fields = ('user__username', 'chat_id')  # Поиск по имени пользователя и chat_id

admin.site.register(CustomUser)