import requests
import json
from telegram import Bot
import os
import asyncio
from functools import wraps
from app.utils.encryption import load_env_encrypted

def async_to_sync(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

@async_to_sync
async def report_error(error_message: str):
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    admin_telegram = config['admin'].get('telegram_chat_id')
    admin_facebook = config['admin'].get('facebook_psid')
    
    error_text = f"⚠️ AlertBot Error:\n{error_message}\n\nPowered by AlertBot"
    
    if admin_telegram:
        try:
            bot = Bot(token=load_env_encrypted('TELEGRAM_BOT_TOKEN', ''))
            await bot.send_message(chat_id=admin_telegram, text=error_text)
        except Exception as e:
            print(f"Failed to send error to Telegram: {e}")
    
    if admin_facebook:
        try:
            fb_token = load_env_encrypted('FACEBOOK_PAGE_TOKEN', '')
            url = f"https://graph.facebook.com/v12.0/me/messages"
            payload = {
                "recipient": {"id": admin_facebook},
                "message": {"text": error_text}
            }
            requests.post(url, params={"access_token": fb_token}, json=payload)
        except Exception as e:
            print(f"Failed to send error to Facebook: {e}")
