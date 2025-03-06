from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки по умолчанию")

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_permissions',
    )

    def __str__(self):
        return self.username

class Product(models.Model):
    """Модель продукта (букета)."""
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение", null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    """Модель заказа."""
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name="Товары")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    delivery_address = models.TextField(verbose_name="Адрес доставки")
    delivery_date = models.DateField(verbose_name="Дата доставки", null=True, blank=True)
    delivery_time = models.TimeField(verbose_name="Время доставки", null=True, blank=True)
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

    @property
    def total_price(self):
        """Вычисляет общую стоимость заказа."""
        return sum(item.product.price * item.quantity for item in self.orderitem_set.all())

class OrderItem(models.Model):
    """Модель элемента заказа."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

class Cart(models.Model):
    """Модель корзины пользователя."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

class CartItem(models.Model):
    """Модель элемента корзины."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

class AdminTelegramUser(models.Model):
    """Модель для связи администраторов с их Telegram chat_id."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="Администратор")
    chat_id = models.BigIntegerField(unique=True, verbose_name="Telegram Chat ID")

    def __str__(self):
        return f"Админ {self.user.username} (Chat ID: {self.chat_id})"