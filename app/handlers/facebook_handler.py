import os
import requests
from app.utils import load_env_encrypted

def send_facebook(recipient: str, message: str) -> dict:
    try:
        token = load_env_encrypted('FACEBOOK_PAGE_TOKEN', '')
        url = f"https://graph.facebook.com/v22.0/me/messages"
        
        formatted_message = (
            f"╭──⦿【 💬 NEW MESSAGE 】\n"
            f"│ 👤 From: AlertBot\n"
            f"│ 📨 Message:\n"
            f"│ {message}\n"
            f"│\n"
            f"│ ⚡ Powered by AlertBot\n"
            f"╰──────⦿"
        )

        payload = {
            "recipient": {"id": recipient},
            "message": {"text": formatted_message}
        }
        
        response = requests.post(
            url,
            params={"access_token": token},
            json=payload
        )
        
        if response.status_code == 200:
            return {"status": "sent", "details": "Facebook message sent successfully"}
        else:
            return {"status": "failed", "details": response.text}
    except Exception as e:
        return {"status": "failed", "details": str(e)}

def handle_facebook_webhook(data: dict) -> dict:
    messaging = data.get('entry', [{}])[0].get('messaging', [{}])[0]
    sender_id = messaging.get('sender', {}).get('id')
    
    if 'postback' in messaging:
        payload = messaging['postback'].get('payload')
        if payload == 'GET_STARTED':
            welcome_message = (
                f"╭──⦿【 ⚡ ALERTBOT 】\n"
                f"│ 👋 Welcome to AlertBot!\n"
                f"│ 🧠 Your PSID: {sender_id}\n"
                f"│ 📡 Use this PSID in your API calls.\n"
                f"│ ⚙️ System: Facebook Messenger v1.0\n"
                f"╰───────⦿"
            )
            return send_facebook(sender_id, welcome_message)
    
    if 'message' in messaging:
        text = messaging['message'].get('text', '')
        if text.lower() == '/getpsid':
            psid_message = (
                f"╭──⦿【 🪪 PSID DETAILS 】\n"
                f"│ 👤 Your PSID: {sender_id}\n"
                f"│ 🌐 Use this PSID in your API calls.\n"
                f"│ ⚡ Powered by AlertBot\n"
                f"╰───────⦿"
            )
            return send_facebook(sender_id, psid_message)
    
    return {"status": "ignored", "details": "Message ignored"}
