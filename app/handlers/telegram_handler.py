import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import asyncio
from app.utils import load_env_encrypted

bot_app = None

async def start_command(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Get My ID", callback_data='getid')],
        [InlineKeyboardButton("Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 Welcome to AlertBot!\n\n"
        "I'm here to deliver important alerts to you.\n\n"
        "Powered by AlertBot",
        reply_markup=reply_markup
    )

async def getid_command(update: Update, context):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"🆔 Your Telegram ID: {user_id}\n\n"
        f"Use this ID in your API calls.\n\n"
        f"Powered by AlertBot"
    )

async def help_command(update: Update, context):
    await update.message.reply_text(
        "📚 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/getid - Get your Telegram ID\n"
        "/help - Show this help\n\n"
        "Powered by AlertBot"
    )

async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'getid':
        user_id = update.effective_user.id
        await query.message.reply_text(
            f"🆔 Your Telegram ID: {user_id}\n\n"
            f"Use this ID in your API calls.\n\n"
            f"Powered by AlertBot"
        )
    elif query.data == 'help':
        await query.message.reply_text(
            "📚 Available Commands:\n\n"
            "/start - Welcome message\n"
            "/getid - Get your Telegram ID\n"
            "/help - Show this help\n\n"
            "Powered by AlertBot"
        )

async def ignore_messages(update: Update, context):
    pass

def setup_telegram_bot():
    global bot_app
    token = load_env_encrypted('TELEGRAM_BOT_TOKEN', '')
    if not token:
        return
    
    bot_app = Application.builder().token(token).build()
    
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("getid", getid_command))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_messages))
    
    asyncio.create_task(bot_app.run_polling(allowed_updates=Update.ALL_TYPES))

async def send_telegram_async(recipient: str, message: str) -> dict:
    try:
        bot = Bot(token=load_env_encrypted('TELEGRAM_BOT_TOKEN', ''))
        await bot.send_message(
            chat_id=recipient,
            text=f"{message}\n\nPowered by AlertBot"
        )
        return {"status": "sent", "details": "Telegram message sent successfully"}
    except Exception as e:
        return {"status": "failed", "details": str(e)}

def send_telegram(recipient: str, message: str) -> dict:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(send_telegram_async(recipient, message))
