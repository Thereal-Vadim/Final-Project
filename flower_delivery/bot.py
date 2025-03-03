import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, JobQueue
import os
from dotenv import load_dotenv
import requests
import json

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота и URL API из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '7942497197:AAEfsz17_cjwea9e7cOlp3N6sLwNyCX6-Zw')  # Замените на ваш токен бота
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000/api/orders/')  # Замените на ваш URL API

# Состояния разговора
NAME, PHONE, ADDRESS, PRODUCTS = range(4)

# Функция для поиска продукта по названию через API
def get_product_by_name(name):
    try:
        response = requests.get(f"{API_URL.replace('orders', 'products')}?name={name}")
        response.raise_for_status()
        data = response.json()  # Получаем JSON-ответ
        # Если API возвращает список напрямую, фильтруем по имени
        products = [p for p in data if p['name'].lower() == name.lower()]
        return products[0] if products else None
    except requests.RequestException as e:
        print(f"Ошибка при поиске продукта: {e}")
        return None

# Обработчик команды /start
async def start(update: Update, context) -> int:
    user = update.message.from_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для заказа цветов.\n"
        "Пожалуйста, введите ваше имя:"
    )
    return NAME

# Обработчик имени
async def name(update: Update, context) -> int:
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "Спасибо! Теперь введите ваш номер телефона (например, +79991234567):"
    )
    return PHONE

# Обработчик телефона
async def phone(update: Update, context) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "Отлично! Введите адрес доставки:"
    )
    return ADDRESS

# Обработчик адреса
async def address(update: Update, context) -> int:
    context.user_data['address'] = update.message.text
    await update.message.reply_text(
        "Выберите букеты (перечислите названия через запятую, например, 'Розы красные, Лилии белые'):"
    )
    return PRODUCTS

# Обработчик выбора продуктов
async def products(update: Update, context) -> int:
    context.user_data['products'] = update.message.text
    user_data = context.user_data
    chat_id = update.effective_chat.id

    # Формируем данные для заказа
    order_data = {
        "user": 1,  # Убедитесь, что пользователь с id=1 существует
        "delivery_address": user_data['address'],
        "status": "pending",
        "orderitem_set": []
    }

    # Парсим список продуктов и добавляем их в orderitem_set
    product_names = [p.strip() for p in user_data['products'].split(',')]
    for name in product_names:
        product = get_product_by_name(name)
        if product:
            print(f"Найден продукт: {product}")  # Отладочный вывод
            order_data["orderitem_set"].append({
                "product": product['id'],
                "quantity": 1  # Можно запросить количество у пользователя для улучшения
            })
        else:
            await update.message.reply_text(f"Продукт '{name}' не найден. Пожалуйста, проверьте названия.")
            return PRODUCTS

    print(f"Отправляем заказ: {order_data}")  # Отладочный вывод перед запросом

    # Отправляем заказ в API
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(API_URL, data=json.dumps(order_data), headers=headers)
        response.raise_for_status()
        order_id = response.json()['id']
        await update.message.reply_text(
            f"Ваш заказ принят!\n"
            f"Номер заказа: {order_id}\n"
            f"Статус заказа будет отправлен позже."
        )
    except requests.RequestException as e:
        await update.message.reply_text(f"Ошибка при сохранении заказа: {e}")
        print(f"Детали ошибки: {e.response.status_code} - {e.response.text if e.response else 'No response'}")  # Дополнительная отладка
        return ConversationHandler.END

    return ConversationHandler.END

    # Парсим список продуктов и добавляем их в orderitem_set
    product_names = [p.strip() for p in user_data['products'].split(',')]
    for name in product_names:
        product = get_product_by_name(name)
        if product:
            order_data["orderitem_set"].append({
                "product": product['id'],
                "quantity": 1  # Можно запросить количество у пользователя для улучшения
            })
        else:
            await update.message.reply_text(f"Продукт '{name}' не найден. Пожалуйста, проверьте названия.")
            return PRODUCTS

    # Отправляем заказ в API
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(API_URL, data=json.dumps(order_data), headers=headers)
        response.raise_for_status()
        order_id = response.json()['id']
        await update.message.reply_text(
            f"Ваш заказ принят!\n"
            f"Номер заказа: {order_id}\n"
            f"Статус заказа будет отправлен позже."
        )
    except requests.RequestException as e:
        await update.message.reply_text(f"Ошибка при сохранении заказа: {e}")
        return ConversationHandler.END

    return ConversationHandler.END

# Обработчик команды /cancel для отмены разговора
async def cancel(update: Update, context) -> int:
    await update.message.reply_text(
        "Диалог отменён. Напишите /start, чтобы начать заново."
    )
    return ConversationHandler.END

# Функция для проверки статуса заказов и отправки уведомлений
async def check_order_status(context):
    try:
        # Получаем все заказы через API
        response = requests.get(API_URL, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        orders = response.json()

        for order in orders:
            chat_id = order['user']['chat_id']  # Здесь нужно хранить chat_id пользователя в модели Order или через отдельную таблицу
            status = order['status']
            order_id = order['id']

            # Отправляем уведомление, если статус изменился
            if status != 'pending':
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"Обновление заказа #{order_id}: Статус — {status}"
                )
    except requests.exceptions.HTTPError as e:
        print(f"HTTP ошибка при проверке статусов: {e.response.status_code} - {e.response.text}")
    except requests.RequestException as e:
        print(f"Ошибка при проверке статусов: {e}")

# Главная функция для запуска бота
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            PRODUCTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, products)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Настройка планировщика для проверки статусов заказов
    job_queue = application.job_queue
    job_queue.run_repeating(check_order_status, interval=300)  # Проверка каждые 5 минут

    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)  # Используем ALL_TYPES вместо ALL

if __name__ == '__main__':
    main()