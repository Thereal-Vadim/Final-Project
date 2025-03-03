from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from rest_framework import viewsets, permissions, response
from .serializers import OrderSerializer, ProductSerializer  # Добавляем импорт ProductSerializer
from .models import Product, Cart, CartItem, Order, OrderItem

@login_required
def catalog(request):
    products = Product.objects.all()
    return render(request, 'flowers/catalog.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    # Вычисляем итоговую сумму для каждого элемента
    for item in items:
        item.total = item.quantity * item.product.price if item.quantity and item.product.price else 0
    return render(request, 'flowers/cart.html', {'items': items})

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)
        order = Order.objects.create(user=request.user, delivery_address=request.POST['address'], status="pending")
        for item in cart.cartitem_set.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart.delete()  # Очистка корзины после оформления
        return redirect('order_history')
    return render(request, 'flowers/checkout.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'flowers/order_history.html', {'orders': orders})

@login_required
def repeat_order(request, order_id):
    old_order = Order.objects.get(id=order_id)
    new_order = Order.objects.create(user=request.user, delivery_address=old_order.delivery_address, status="pending")
    for item in old_order.orderitem_set.all():
        OrderItem.objects.create(order=new_order, product=item.product, quantity=item.quantity)
    return redirect('order_history')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Cart.objects.get_or_create(user=user)  # Создаём корзину для нового пользователя
            return redirect('catalog')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# API для продуктов
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer  # Теперь импортирован
    permission_classes = [permissions.AllowAny]  # Доступен всем для поиска

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        if name:
            return Product.objects.filter(name__icontains=name)
        return Product.objects.all()

# API для заказов
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # Временно разрешить доступ всем для тестирования

    def get_queryset(self):
        return Order.objects.all()  # Для тестов возвращаем все заказы (в продакшне ограничьте по пользователю)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return response.Response(serializer.data, status=201)