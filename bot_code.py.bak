from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import Text, COMMAND
from telegram import ReplyKeyboardMarkup, KeyboardButton
from sheets_code import add_article, add_goal, get_articles, get_goals, clear_sheet
import os

def run():
    app = Application.builder().token("7281433062:AAGozy3VnJ-o7IxUjO16rWOgJLLXw-K-OMM").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(Text() & ~COMMAND, handle_message))
    webhook_url = "https://balcheg-bot-1.onrender.com/telegram"
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path="telegram",
        webhook_url=webhook_url
    )
    app.run_forever()

async def start(update, context):
    keyboard = [["➕ Добавить статью", "✅ Добавить задачу"], ["📖 Показать статьи", "📋 Показать задачи"], ["🧼 Очистить статьи", "🧼 Очистить задачи"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)

async def menu(update, context):
    await start(update, context)

async def handle_message(update, context):
    message = update.message.text
    username = update.message.from_user.username or update.message.from_user.first_name
    try:
        if 'action' in context.user_data:
            if context.user_data['action'] == 'add_article':
                add_article(message, username)
                await update.message.reply_text("✅ Статья добавлена.")
            elif context.user_data['action'] == 'add_task':
                add_goal(message, username)
                await update.message.reply_text("✅ Задача добавлена.")
            context.user_data.clear()
        else:
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
                    await update.message.reply_text(f"📖 Статьи:\n{response}")
                else:
                    await update.message.reply_text("Пока нет статей.")
            elif message == "📋 Показать задачи":
                tasks = get_goals()
                if tasks:
                    response = "\n".join([f"{row[0]}: {row[1]} (добавил: {row[2]})" for row in tasks if len(row) >= 3])
                    await update.message.reply_text(f"📋 Задачи:\n{response}")
                else:
                    await update.message.reply_text("Пока нет задач.")
            elif message == "🧼 Очистить статьи":
                clear_sheet('Articles')
                await update.message.reply_text("🧼 Список статей очищен.")
            elif message == "🧼 Очистить задачи":
                clear_sheet('Goals')
                await update.message.reply_text("🧼 Список задач очищен.")
            else:
                await update.message.reply_text("🤖 Используй кнопки для действий.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")

if __name__ == "__main__":
    run()