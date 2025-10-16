import os
import requests

def send_facebook(recipient: str, message: str) -> dict:
    try:
        token = os.getenv('FACEBOOK_PAGE_TOKEN')
        url = f"https://graph.facebook.com/v12.0/me/messages"
        
        payload = {
            "recipient": {"id": recipient},
            "message": {
                "text": f"{message}\n\nPowered by AlertBot"
            }
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
            return send_facebook(sender_id, f"Welcome to AlertBot!\nYour PSID: {sender_id}\nUse this PSID in your API calls.")
    
    if 'message' in messaging:
        text = messaging['message'].get('text', '')
        if text.lower() == '/getpsid':
            return send_facebook(sender_id, f"Your PSID: {sender_id}\nUse this PSID in your API calls.")
    
    return {"status": "ignored", "details": "Message ignored"}
