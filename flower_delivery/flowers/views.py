import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.conf import settings
import requests
import json
from .models import Product, Cart, CartItem, Order, OrderItem, AdminTelegramUser
from .forms import CustomUserCreationForm  # Импортируйте кастомную форму

@login_required
def catalog(request):
    """Отображает каталог продуктов."""
    products = Product.objects.all()
    return render(request, 'flowers/catalog.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    """Добавляет продукт в корзину."""
    try:
        product = Product.objects.get(id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
    except Product.DoesNotExist:
        return redirect('catalog')
    return redirect('cart')

@login_required
def cart(request):
    """Отображает содержимое корзины."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    for item in items:
        item.total = item.quantity * item.product.price if item.quantity and item.product.price else 0
    return render(request, 'flowers/cart.html', {'items': items})

@login_required
def checkout(request):
    """Оформляет заказ и отправляет уведомление в Telegram."""
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            order = Order.objects.create(
                user=request.user,
                delivery_address=request.POST['address'],
                status='pending',
                delivery_date=request.POST.get('delivery_date'),
                delivery_time=request.POST.get('delivery_time'),
                comment=request.POST.get('comment')
            )
            for item in cart.cartitem_set.all():
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            cart.delete()

            # Подготовка и отправка уведомления
            message = _prepare_telegram_message(order, request)
            _send_telegram_notification_to_admins(message, order)

            return redirect('order_history')
        except Exception as e:
            return render(request, 'flowers/checkout.html', {'error': str(e)})

    return render(request, 'flowers/checkout.html')

@login_required
def order_history(request):
    """Отображает историю заказов пользователя."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'flowers/order_history.html', {'orders': orders})

@login_required
def repeat_order(request, order_id):
    """Повторяет существующий заказ."""
    try:
        old_order = Order.objects.get(id=order_id, user=request.user)
        new_order = Order.objects.create(
            user=request.user,
            delivery_address=old_order.delivery_address,
            status='pending'
        )
        for item in old_order.orderitem_set.all():
            OrderItem.objects.create(order=new_order, product=item.product, quantity=item.quantity)
        return redirect('order_history')
    except Order.DoesNotExist:
        return redirect('order_history')

def register(request):
    """Регистрирует нового пользователя."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Используем кастомную форму
        if form.is_valid():
            user = form.save()
            login(request, user)
            Cart.objects.get_or_create(user=user)
            return redirect('catalog')
    else:
        form = CustomUserCreationForm()  # Используем кастомную форму
    return render(request, 'registration/register.html', {'form': form})

# Вспомогательные функции
def _prepare_telegram_message(order, request):
    """Подготавливает сообщение для Telegram."""
    total_price = order.total_price
    message = f"Новый заказ #{order.id}\n"
    message += f"Клиент: {order.user.username}\n"
    message += f"Телефон: {order.user.phone if order.user.phone else 'Не указан'}\n"
    message += f"Адрес доставки: {order.delivery_address}\n"
    message += f"Дата доставки: {order.delivery_date or 'Не указана'}\n"
    message += f"Время доставки: {order.delivery_time or 'Не указано'}\n"
    message += f"Стоимость: {total_price} руб.\n"
    if order.comment:
        message += f"Комментарий: {order.comment}\n"
    return message

def _send_telegram_notification_to_admins(message, order):
    """Отправляет уведомление всем администраторам в Telegram."""
    bot_token = os.getenv('BOT_TOKEN', '')
    if not bot_token:
        print("Ошибка: BOT_TOKEN не указан в .env")
        return

    admins = AdminTelegramUser.objects.all()
    for admin in admins:
        chat_id = admin.chat_id
        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, data=json.dumps({'chat_id': chat_id, 'text': message}), headers=headers)

        if response.status_code != 200:
            print(f"Ошибка отправки сообщения админу {admin.user.username}: {response.status_code} - {response.text}")

        first_item = order.orderitem_set.first()
        if first_item and first_item.product.image:
            photo_url = request.build_absolute_uri(first_item.product.image.url)
            photo_api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            photo_response = requests.post(photo_api_url, data={'chat_id': chat_id, 'photo': photo_url, 'caption': message})
            if photo_response.status_code != 200:
                print(f"Ошибка отправки фото админу {admin.user.username}: {photo_response.status_code} - {photo_response.text}")