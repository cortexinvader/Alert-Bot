import os
import time
import threading
import logging
from typing import Any, Dict, Optional

import requests

from app.utils import load_env_encrypted

logger = logging.getLogger(__name__)

# Public functions used by routes and other modules
__all__ = [
    "send_facebook",
    "handle_messenger_event",
    "facebook_startup_check",
    "start_facebook_monitor",
    "subscribe_page_if_configured",
]


def _format_alert_message(message: str) -> str:
    return (
        f"╭─⦿【💬 NEW MESSAGE】\n"
        f"│ {message}\n"
        f"│\n"
        f"│ ⚡ Powered by AlertBot\n"
        f"╰────────⦿\n"
        f"• In relations to Facebook Policy users are advised to message bot at least between 24hrs interval"
    )


def send_facebook(recipient: str, message: str) -> Dict[str, Any]:
    """
    Send a plain text message to a Facebook PSID using the page access token.
    Returns a dict with status/details similar to other handlers.
    """
    try:
        token = load_env_encrypted('FACEBOOK_PAGE_TOKEN', '')
        if not token:
            return {"status": "failed", "details": "FACEBOOK_PAGE_TOKEN not set"}

        url = f"https://graph.facebook.com/v22.0/me/messages"

        formatted_message = _format_alert_message(message)

        payload = {
            "recipient": {"id": recipient},
            "message": {"text": formatted_message}
        }

        response = requests.post(
            url,
            params={"access_token": token},
            json=payload,
            timeout=10
        )

        if response.status_code in (200, 201):
            return {"status": "sent", "details": "Facebook message sent successfully"}
        else:
            # Surface Graph API error text for debugging
            return {"status": "failed", "details": response.text}
    except Exception as e:
        logger.exception("send_facebook error")
        return {"status": "failed", "details": str(e)}


def handle_messenger_event(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse an incoming Messenger webhook payload and handle basic interactions
    (Get Started postback / /getpsid text command). This function returns the
    result from send_facebook when it sends a reply, or None when nothing was sent.
    Expected to be called from your Flask webhook route (routes.py).
    """
    try:
        entry = data.get('entry', [])
        if not entry:
            return None

        messaging = entry[0].get('messaging', [])
        if not messaging:
            return None

        ms = messaging[0]
        sender_id = ms.get('sender', {}).get('id')
        if not sender_id:
            return None

        # Handle postbacks (e.g., Get Started)
        postback = ms.get('postback')
        if postback:
            payload = postback.get('payload')
            if payload == 'GET_STARTED':
                welcome_message = (
                    f"╭─⦿【 ⚡ ALERTBOT 】\n"
                    f"│ 👋 Welcome to AlertBot!\n"
                    f"│ 🧠 Your PSID: {sender_id}\n"
                    f"│ 📡 Use this PSID in your API calls.\n"
                    f"│ ⚙️ System: Facebook Messenger v1.0\n"
                    f"╰───────⦿"
                )
                return send_facebook(sender_id, welcome_message)
            # add more postback handling here if needed

        # Handle text messages (commands)
        message = ms.get('message')
        if message:
            text = message.get('text', '')
            if text and text.strip().lower() == '/getpsid':
                psid_message = (
                    f"╭─⦿【🪪FACEBOOK PSID】\n"
                    f"│ 👤 Your PSID: {sender_id}\n"
                    f"│ 🌐 Use this PSID in your API calls.\n"
                    f"│ ⚡ Powered by AlertBot\n"
                    f"╰────────⦿"
                )
                return send_facebook(sender_id, psid_message)

        return None
    except Exception:
        logger.exception("Failed to handle messenger event")
        return None


# --- Startup / health / subscription helpers ---


def facebook_startup_check() -> Dict[str, Any]:
    """
    Lightweight check to validate the page access token and (optionally)
    return important details. This does NOT change webhook configuration.
    Returns a dict with keys: ok (bool) and details (str).
    """
    token = load_env_encrypted('FACEBOOK_PAGE_TOKEN', '')
    if not token:
        return {"ok": False, "details": "FACEBOOK_PAGE_TOKEN not set"}

    try:
        resp = requests.get("https://graph.facebook.com/v22.0/me", params={"access_token": token}, timeout=5)
        if resp.status_code == 200:
            body = resp.json()
            name = body.get('name', 'unknown')
            id_ = body.get('id', '')
            details = f"token valid for page: {name} ({id_})"
            return {"ok": True, "details": details, "page_name": name, "page_id": id_}
        else:
            return {"ok": False, "details": resp.text}
    except Exception as e:
        logger.exception("facebook_startup_check failed")
        return {"ok": False, "details": str(e)}


def subscribe_page_if_configured() -> Dict[str, Any]:
    """
    If FACEBOOK_PAGE_ID and FACEBOOK_PAGE_TOKEN are configured, attempt to
    subscribe the page to the 'messages' and 'messaging_postbacks' fields so
    postbacks/Get Started flows will arrive at the webhook. Returns a dict
    describing success/failure.
    """
    token = load_env_encrypted('FACEBOOK_PAGE_TOKEN', '')
    page_id = os.getenv('FACEBOOK_PAGE_ID') or load_env_encrypted('FACEBOOK_PAGE_ID', '')

    if not token:
        return {"ok": False, "details": "FACEBOOK_PAGE_TOKEN not set"}
    if not page_id:
        return {"ok": False, "details": "FACEBOOK_PAGE_ID not set; cannot subscribe automatically"}

    try:
        url = f"https://graph.facebook.com/v22.0/{page_id}/subscribed_apps"
        params = {"access_token": token, "subscribed_fields": "messages,messaging_postbacks"}
        resp = requests.post(url, params=params, timeout=10)
        if resp.status_code in (200, 201):
            return {"ok": True, "details": "page subscribed to messaging events", "response": resp.json()}
        else:
            return {"ok": False, "details": resp.text}
    except Exception as e:
        logger.exception("subscribe_page_if_configured failed")
        return {"ok": False, "details": str(e)}


def _facebook_monitor_loop(interval_seconds: int = 600):
    """
    Background monitor loop that periodically validates the token and attempts
    to subscribe the page if a PAGE_ID is provided. Runs forever as a daemon thread.
    """
    while True:
        try:
            status = facebook_startup_check()
            if not status.get("ok"):
                logger.warning("Facebook startup check failed: %s", status.get("details"))
            else:
                logger.info("Facebook token check OK: %s", status.get("details"))
                # Try subscription if page id provided
                sub = subscribe_page_if_configured()
                if sub.get("ok"):
                    logger.info("Facebook page subscription: %s", sub.get("details"))
                else:
                    # Only warn; subscription can also be configured manually via FB dashboard
                    logger.debug("Facebook subscription attempt result: %s", sub.get("details"))
        except Exception:
            logger.exception("Unhandled error in facebook monitor loop")

        # Sleep until next check
        try:
            time.sleep(interval_seconds)
        except Exception:
            # If sleep is interrupted, loop will repeat
            pass


def start_facebook_monitor(interval_seconds: int = 600) -> threading.Thread:
    """
    Start the background monitor in a daemon thread. The monitor performs an
    initial token validation and subscription attempt, then repeats every
    interval_seconds. Returns the Thread object.
    """
    t = threading.Thread(target=_facebook_monitor_loop, args=(interval_seconds,), daemon=True)
    t.start()
    logger.info("Started Facebook monitor thread (interval %ss)", interval_seconds)
    return t
