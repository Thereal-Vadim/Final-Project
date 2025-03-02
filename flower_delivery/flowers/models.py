from django.db import models
from django.contrib.auth.models import User


# Модель товара (цветы)
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение", null=True, blank=True)

    def __str__(self):
        return self.name


# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name="Товары")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    delivery_address = models.TextField(verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"


# Промежуточная модель для связи товаров и заказов (с количеством)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")


# Модель корзины (временное хранение до оформления заказа)
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")