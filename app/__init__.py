from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import json
import threading

load_dotenv()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

_initialized = False


def init_default_keys():
    """Initialize API keys from key.txt only if they don’t already exist."""
    from app.models import get_session, APIKey
    db = get_session()

    # Read keys from key.txt
    if os.path.exists('key.txt'):
        with open('key.txt', 'r') as f:
            keys = [line.strip() for line in f if line.strip()]
        
        for key in keys:
            # Only add if not already present
            exists = db.query(APIKey).filter_by(key=key).first()
            if not exists:
                db.add(APIKey(key=key))
        
        db.commit()
    db.close()


def create_app():
    global _initialized

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///alertbot.db')

    CORS(app)
    limiter.init_app(app)

    from app.models import init_db
    init_db()

    from app.routes import register_routes
    register_routes(app)

    if not _initialized:
        _initialized = True

        init_default_keys()

        from app.queue import start_scheduler
        start_scheduler()

        from app.handlers import setup_telegram_bot
        telegram_thread = threading.Thread(target=setup_telegram_bot, daemon=True)
        telegram_thread.start()

    return app
