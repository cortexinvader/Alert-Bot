from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import threading
from sqlalchemy import inspect

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

_initialized = False


def safe_init_db(engine, Base):
    """Create only missing tables to avoid 'already exists' errors."""
    inspector = inspect(engine)
    existing = inspector.get_table_names()

    missing = [t.name for t in Base.metadata.sorted_tables if t.name not in existing]
    if missing:
        print(f"🧱 Creating missing tables: {missing}")
        Base.metadata.create_all(engine)
    else:
        print("✅ All tables already exist — skipping creation.")


def init_default_keys():
    """Initialize API keys from key.txt if not already in DB."""
    from app.models import get_session, APIKey
    db = get_session()

    if os.path.exists('key.txt'):
        with open('key.txt', 'r') as f:
            keys = [line.strip() for line in f if line.strip()]

        for key in keys:
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

    # ✅ Safe DB initialization
    from app.models import Base, engine
    safe_init_db(engine, Base)

    from app.routes import register_routes
    register_routes(app)

    if not _initialized:
        _initialized = True

        init_default_keys()

        from app.queue import start_scheduler
        start_scheduler()

        from app.handlers import setup_telegram_bot
        threading.Thread(target=setup_telegram_bot, daemon=True).start()

    return app
