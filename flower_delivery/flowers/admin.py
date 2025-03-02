from django.contrib import admin
from .models import Product, Order, OrderItem, Cart, CartItem

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')  # Поля для отображения
    list_editable = ('status',)  # Поле, которое можно редактировать прямо в списке