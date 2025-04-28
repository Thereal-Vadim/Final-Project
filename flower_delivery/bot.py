import os
import django
from dotenv import load_dotenv
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from asgiref.sync import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
django.setup()

# Импорт моделей после настройки Django
from flowers.models import Order, AdminTelegramUser

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env")

# Состояния для команды /setstatus
SET_ORDER_ID, SET_STATUS = range(2)

# Асинхронная проверка, является ли пользователь администратором
async def is_admin_chat(chat_id):
    return await sync_to_async(lambda: AdminTelegramUser.objects.filter(chat_id=chat_id).exists(), thread_sensitive=True)()

# Команда /start
async def start(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    is_admin = await is_admin_chat(chat_id)
    if not is_admin:
        await update.message.reply_text("У вас нет прав администратора.")
        return
    await update.message.reply_text(
        "Привет, администратор! Доступные команды:\n"
        "/orders - Показать все заказы\n"
        "/setstatus <order_id> <status> - Изменить статус заказа\n"
        "/help - Показать помощь"
    )

# Команда /orders
async def list_orders(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    is_admin = await is_admin_chat(chat_id)
    if not is_admin:
        await update.message.reply_text("У вас нет прав администратора.")
        return
    orders = await sync_to_async(list)(Order.objects.all())
    if not orders:
        await update.message.reply_text("Нет заказов.")
        return
    message = "Список заказов:\n"
    for order in orders:
        message += f"#{order.id} - {order.status} ({order.created_at})\n"
        message += f"Клиент: {order.user.username}\nАдрес: {order.delivery_address}\n"
        message += f"Стоимость: {order.total_price} руб.\n\n"
    await update.message.reply_text(message)

# Команда /setstatus
async def set_status_start(update: Update, context) -> int:
    chat_id = update.effective_chat.id
    is_admin = await is_admin_chat(chat_id)
    if not is_admin:
        await update.message.reply_text("У вас нет прав администратора.")
        return ConversationHandler.END
    await update.message.reply_text("Введите ID заказа:")
    return SET_ORDER_ID

async def set_status_order_id(update: Update, context) -> int:
    context.user_data['order_id'] = update.message.text
    await update.message.reply_text("Введите новый статус (pending, delivered, canceled):")
    return SET_STATUS

async def set_status_status(update: Update, context) -> int:
    order_id = context.user_data['order_id']
    new_status = update.message.text.lower()
    if new_status not in dict(Order.STATUS_CHOICES):
        await update.message.reply_text("Неверный статус. Используйте: pending, delivered, canceled.")
        return ConversationHandler.END
    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
        order.status = new_status
        await sync_to_async(order.save)()
        message = f"Статус заказа #{order_id} изменён на {new_status}.\n"
        message += f"Клиент: {order.user.username}\nАдрес: {order.delivery_address}"
        await update.message.reply_text(message)
    except Order.DoesNotExist:
        await update.message.reply_text("Заказ не найден.")
    return ConversationHandler.END

# Команда /help
async def help_command(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    is_admin = await is_admin_chat(chat_id)
    if not is_admin:
        await update.message.reply_text("У вас нет прав администратора.")
        return
    await update.message.reply_text(
        "Доступные команды:\n"
        "/orders - Показать все заказы\n"
        "/setstatus - Изменить статус заказа\n"
        "/help - Показать эту помощь"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик изменения статуса
    status_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('setstatus', set_status_start)],
        states={
            SET_ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_status_order_id)],
            SET_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_status_status)],
        },
        fallbacks=[],
    )

    # Регистрация обработчиков
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('orders', list_orders))
    application.add_handler(status_conv_handler)
    application.add_handler(CommandHandler('help', help_command))

    # Запуск бота
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == '__main__':
    main()