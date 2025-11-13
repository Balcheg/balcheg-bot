from telegram.ext import Application, CommandHandler, MessageHandler
from telegram.ext.filters import Text, COMMAND
from telegram import ReplyKeyboardMarkup, Update
from sheets_code import add_article, add_goal, get_articles, get_goals, clear_sheet
import os
import asyncio
from aiohttp import web

# ====== WEBHOOK И НАСТРОЙКА AIOHTTP ======

async def health_check(request):
    """Проверка работоспособности Render."""
    return web.Response(text="OK", status=200)

async def telegram_webhook(request):
    """Обработка входящих апдейтов от Telegram."""
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK", status=200)

async def setup_application():
    """Создание Telegram-приложения и регистрация обработчиков."""
    global app
    app = Application.builder().token("7281433062:AAGozy3VnJ-o7IxUjO16rWOgJLLXw-K-OMM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(Text() & ~COMMAND, handle_message))

    await app.initialize()

async def run():
    """Запуск Telegram webhook и HTTP-сервера."""
    await setup_application()

    web_app = web.Application()
    web_app.router.add_get("/health", health_check)
    web_app.router.add_post("/telegram", telegram_webhook)

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"✅ Бот запущен и слушает порт {port}")
    await asyncio.Event().wait()

# ====== ОСНОВНОЕ МЕНЮ ======

def get_main_menu():
    """Возвращает клавиатуру основного меню."""
    keyboard = [
        ["➕ Добавить статью", "✅ Добавить задачу"],
        ["📖 Показать статьи", "📋 Показать задачи"],
        ["🧼 Очистить статьи", "🧼 Очистить задачи"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update, context):
    """Главное меню (без текста)."""
    await update.message.reply_text(" ", reply_markup=get_main_menu())

async def menu(update, context):
    """Команда /menu — просто показывает меню."""
    await update.message.reply_text(" ", reply_markup=get_main_menu())

# ====== ЛОГИКА ОБРАБОТКИ СООБЩЕНИЙ ======

async def handle_message(update, context):
    """Главный обработчик всех текстовых сообщений."""
    message = update.message.text
    username = update.message.from_user.username or update.message.from_user.first_name

    try:
        # Если пользователь добавляет статью или задачу
        if 'action' in context.user_data:
            if context.user_data['action'] == 'add_article':
                add_article(message, username)
                await update.message.reply_text("✅ Статья добавлена.", reply_markup=get_main_menu())
            elif context.user_data['action'] == 'add_task':
                add_goal(message, username)
                await update.message.reply_text("✅ Задача добавлена.", reply_markup=get_main_menu())
            context.user_data.clear()
            return

        # === ДОБАВЛЕНИЕ ===
        if message == "➕ Добавить статью":
            context.user_data['action'] = 'add_article'
            await update.message.reply_text("✍️ Напиши текст статьи:")

        elif message == "✅ Добавить задачу":
            context.user_data['action'] = 'add_task'
            await update.message.reply_text("✍️ Напиши текст задачи:")

        # === ПРОСМОТР ===
        elif message == "📖 Показать статьи":
            articles = get_articles()
            if articles:
                response = "\n".join([f"{row[0]}: {row[1]} (добавил: {row[2]})"
                                      for row in articles if len(row) >= 3])
                await update.message.reply_text(f"📖 Статьи:\n{response}", reply_markup=get_main_menu())
            else:
                await update.message.reply_text("Пока нет статей.", reply_markup=get_main_menu())

        elif message == "📋 Показать задачи":
            tasks = get_goals()
            if tasks:
                response = "\n".join([f"{row[0]}: {row[1]} (добавил: {row[2]})"
                                      for row in tasks if len(row) >= 3])
                await update.message.reply_text(f"📋 Задачи:\n{response}", reply_markup=get_main_menu())
            else:
                await update.message.reply_text("Пока нет задач.", reply_markup=get_main_menu())

        # === ПОДТВЕРЖДЕНИЕ ОЧИСТКИ ===
        elif message == "🧼 Очистить статьи":
            context.user_data['confirm_clear'] = 'Articles'
            keyboard = [["Да Очистить!", "Нет Оставить!"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("❗ Точно очистить статьи? Не промахнулись?", reply_markup=reply_markup)

        elif message == "🧼 Очистить задачи":
            context.user_data['confirm_clear'] = 'Goals'
            keyboard = [["Да Очистить!", "Нет Оставить!"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("❗ Точно очистить задачи? Не промахнулись?", reply_markup=reply_markup)

        # === ПОДТВЕРЖДЕНИЕ ===
        elif message == "Да Очистить!":
            if 'confirm_clear' in context.user_data:
                target = context.user_data['confirm_clear']
                clear_sheet(target)
                await update.message.reply_text(
                    f"🧼 Список {'статей' if target == 'Articles' else 'задач'} очищен.",
                    reply_markup=get_main_menu()
                )
                context.user_data.pop('confirm_clear', None)

        elif message == "Нет Оставить!":
            await update.message.reply_text("🙂 Оставил всё как есть.", reply_markup=get_main_menu())
            context.user_data.pop('confirm_clear', None)

        # === ОСТАЛЬНОЕ ===
        else:
            await update.message.reply_text("🤖 Используй кнопки для действий.", reply_markup=get_main_menu())

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}", reply_markup=get_main_menu())

# ====== ЗАПУСК ======

if __name__ == "__main__":
    asyncio.run(run())
