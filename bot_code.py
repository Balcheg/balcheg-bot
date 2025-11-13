from telegram.ext import Application, CommandHandler, MessageHandler
from telegram.ext.filters import Text, COMMAND
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from sheets_code import add_article, add_goal, get_articles, get_goals, clear_sheet
import os
import asyncio
from aiohttp import web

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def main_menu_keyboard():
    """Возвращает клавиатуру основного меню без текста 'Выбери действие'"""
    keyboard = [
        ["➕ Добавить статью", "✅ Добавить задачу"],
        ["📖 Показать статьи", "📋 Показать задачи"],
        ["🧼 Очистить статьи", "🧼 Очистить задачи"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== СЕРВЕР И ВЕБХУК ==========
async def health_check(request):
    """Проверка, что сервер жив"""
    return web.Response(text="OK", status=200)

async def telegram_webhook(request):
    """Обработка входящих обновлений от Telegram"""
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK", status=200)

async def setup_application():
    """Настраивает Telegram-приложение"""
    global app
    app = Application.builder().token("7281433062:AAGozy3VnJ-o7IxUjO16rWOgJLLXw-K-OMM").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(Text() & ~COMMAND, handle_message))
    await app.initialize()

async def run():
    """Запускает сервер на Render"""
    await setup_application()

    web_app = web.Application()
    web_app.router.add_get("/health", health_check)
    web_app.router.add_post("/telegram", telegram_webhook)

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await asyncio.Event().wait()

# ========== ОСНОВНАЯ ЛОГИКА ==========
async def start(update, context):
    """Стартовая команда — просто показывает клавиатуру"""
    await update.message.reply_text("Привет! 👋", reply_markup=main_menu_keyboard())

async def menu(update, context):
    """Возврат в меню (без текста 'Выбери действие')"""
    await update.message.reply_text("", reply_markup=main_menu_keyboard())

async def handle_message(update, context):
    """Обработка сообщений"""
    message = update.message.text
    username = update.message.from_user.username or update.message.from_user.first_name

    try:
        # Проверяем, ожидается ли ввод от пользователя
        if 'action' in context.user_data:
            if context.user_data['action'] == 'add_article':
                add_article(message, username)
                await update.message.reply_text("✅ Статья добавлена.", reply_markup=main_menu_keyboard())
            elif context.user_data['action'] == 'add_task':
                add_goal(message, username)
                await update.message.reply_text("✅ Задача добавлена.", reply_markup=main_menu_keyboard())
            context.user_data.clear()
            return  # выходим, чтобы не писать лишнего

        # Кнопки основного меню
        if message == "➕ Добавить статью":
            context.user_data['action'] = 'add_article'
            await update.message.reply_text("✍️ Напиши текст статьи:")
        elif message == "✅ Добавить задачу":
            context.user_data['action'] = 'add_task'
            await update.message.reply_text("✅ Напиши текст задачи:")
        elif message == "📖 Показать статьи":
            articles = get_articles()
            if articles:
                response = "\n".join([f"{row[0]}: {row[1]} (добавил: {row[2]})" for row in articles if len(row) >= 3])
                await update.message.reply_text(f"📖 Статьи:\n{response}", reply_markup=main_menu_keyboard())
            else:
                await update.message.reply_text("Пока нет статей.", reply_markup=main_menu_keyboard())
        elif message == "📋 Показать задачи":
            tasks = get_goals()
            if tasks:
                response = "\n".join([f"{row[0]}: {row[1]} (добавил: {row[2]})" for row in tasks if len(row) >= 3])
                await update.message.reply_text(f"📋 Задачи:\n{response}", reply_markup=main_menu_keyboard())
            else:
                await update.message.reply_text("Пока нет задач.", reply_markup=main_menu_keyboard())
        elif message == "🧼 Очистить статьи":
            context.user_data['confirm_clear'] = 'Articles'
            await update.message.reply_text(
                "⚠️ Точно очистить список статей?",
                reply_markup=ReplyKeyboardMarkup([["Да, очистить!", "Нет, оставить!"]], resize_keyboard=True)
            )
        elif message == "🧼 Очистить задачи":
            context.user_data['confirm_clear'] = 'Goals'
            await update.message.reply_text(
                "⚠️ Точно очистить список задач?",
                reply_markup=ReplyKeyboardMarkup([["Да, очистить!", "Нет, оставить!"]], resize_keyboard=True)
            )
        elif message == "Да, очистить!":
            if 'confirm_clear' in context.user_data:
                clear_sheet(context.user_data['confirm_clear'])
                context.user_data.clear()
                await update.message.reply_text("🧼 Список очищен.", reply_markup=main_menu_keyboard())
        elif message == "Нет, оставить!":
            context.user_data.clear()
            await update.message.reply_text("❎ Отменено.", reply_markup=main_menu_keyboard())
        else:
            await update.message.reply_text("🤖 Используй кнопки для действий.", reply_markup=main_menu_keyboard())

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}", reply_markup=main_menu_keyboard())

if __name__ == "__main__":
    asyncio.run(run())
