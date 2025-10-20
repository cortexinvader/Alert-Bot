import threading
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.utils import load_env_encrypted

bot_app = None

async def start_command(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Get My ID", callback_data='getid')],
        [InlineKeyboardButton("Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "╭──⦿【 ⚡ ALERTBOT 】\n"
        "│ 👋 Welcome to AlertBot!\n"
        "│ 🧠 I’m here to deliver important alerts to you.\n"
        "│ 📡 Platform: Telegram\n"
        "│ ⚙️ Version: v1.0\n"
        "╰────────⦿"
    )
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def getid_command(update: Update, context):
    user_id = update.effective_user.id
    message = (
        f"╭──⦿【 🪪 TELEGRAM ID 】\n"
        f"│ 👤 Your Telegram ID: {user_id}\n"
        f"│ 🌐 Use this ID in your API calls.\n"
        f"│ ⚡ Powered by AlertBot\n"
        f"╰────────⦿"
    )
    await update.message.reply_text(message)

async def help_command(update: Update, context):
    message = (
        "╭──⦿【 📚 COMMAND LIST 】\n"
        "│ /start - Display welcome message\n"
        "│ /getid - Show your Telegram ID\n"
        "│ /help  - Show this help menu\n"
        "│\n"
        "│ ⚡ Powered by AlertBot\n"
        "╰────────⦿"
    )
    await update.message.reply_text(message)

async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'getid':
        user_id = update.effective_user.id
        message = (
            f"╭──⦿【 🪪 TELEGRAM ID 】\n"
            f"│ 👤 Your Telegram ID: {user_id}\n"
            f"│ 🌐 Use this ID in your API calls.\n"
            f"│ ⚡ Powered by AlertBot\n"
            f"╰────────⦿"
        )
        await query.message.reply_text(message)
    elif query.data == 'help':
        message = (
            "╭──⦿【 📚 COMMAND LIST 】\n"
            "│ /start - Display welcome message\n"
            "│ /getid - Show your Telegram ID\n"
            "│ /help  - Show this help menu\n"
            "│\n"
            "│ ⚡ Powered by AlertBot\n"
            "╰────────⦿"
        )
        await query.message.reply_text(message)

async def ignore_messages(update: Update, context):
    # intentionally ignore plain text messages (bot is only for commands)
    return

def setup_telegram_bot():
    """
    Build and return the telegram Application (do NOT start polling here).
    Returns the Application instance or None if token missing.
    """
    global bot_app
    token = load_env_encrypted('TELEGRAM_BOT_TOKEN', '')
    if not token:
        return None
    
    bot_app = Application.builder().token(token).build()
    
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("getid", getid_command))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_messages))
    
    return bot_app

def start_telegram_polling(app: Application):
    """
    Run the Application.run_polling() in a dedicated thread.
    Intended to be invoked inside threading.Thread(target=...).
    """
    try:
        # Manually create and set event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run polling with signal handling disabled (required for threading)
        loop.run_until_complete(app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
            stop_signals=None
        ))
    except Exception as e:
        print(f"Telegram polling error: {e}")
    finally:
        try:
            loop.close()
        except:
            pass

def start_telegram_in_thread():
    """
    Convenience: build the Application and start polling in a daemon thread.
    Returns the Thread object or None if token missing.
    """
    app = setup_telegram_bot()
    if app is None:
        return None
    t = threading.Thread(target=start_telegram_polling, args=(app,), daemon=True)
    t.start()
    return t

async def send_telegram_async(recipient: str, message: str) -> dict:
    try:
        formatted_message = (
            f"╭──⦿【 💬 NEW MESSAGE 】\n"
            f"│ 👤 From: AlertBot\n"
            f"│ 📨 Message:\n"
            f"│ {message}\n"
            f"│\n"
            f"│ ⚡ Powered by AlertBot\n"
            f"╰────────⦿"
        )
        bot = Bot(token=load_env_encrypted('TELEGRAM_BOT_TOKEN', ''))
        await bot.send_message(chat_id=recipient, text=formatted_message)
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
