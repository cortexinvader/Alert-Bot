import logging
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import threading
from sqlalchemy import inspect
from sqlalchemy import create_engine

# Setup logging with emoji-friendly format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

load_dotenv()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

_initialized = False

def safe_init_db(engine, Base):
    from sqlalchemy.exc import OperationalError
    inspector = inspect(engine)
    try:
        existing_tables = inspector.get_table_names()
    except Exception:
        existing_tables = []

    missing = [t.name for t in Base.metadata.sorted_tables if t.name not in existing_tables]

    if not missing:
        logger.info("✅ All tables already exist — skipping creation.")
        return

    logger.info(f"🧱 Creating missing tables: {missing}")

    try:
        Base.metadata.create_all(engine, checkfirst=True)
    except OperationalError as e:
        msg = str(e).lower()
        if "already exists" in msg and "table" in msg:
            logger.warning("⚠️ Detected concurrent table creation. Re-checking...")
            inspector = inspect(engine)
            try:
                existing_tables_after = inspector.get_table_names()
            except Exception:
                existing_tables_after = []

            still_missing = [t.name for t in Base.metadata.sorted_tables if t.name not in existing_tables_after]
            if still_missing:
                try:
                    Base.metadata.create_all(engine, checkfirst=True)
                except Exception:
                    logger.error("❌ Retry failed while creating missing tables. Raising exception.")
                    raise
            else:
                logger.info("✅ All tables exist after concurrent creation — continuing.")
        else:
            raise

def init_default_keys():
    from app.models import get_session, APIKey
    db = get_session()

    if not os.path.exists('key.txt'):
        logger.info("🔑 key.txt not found — skipping default keys initialization.")
        db.close()
        return

    with open('key.txt', 'r') as f:
        keys = [line.strip() for line in f if line.strip()]

    for key in keys:
        exists = db.query(APIKey).filter_by(key=key).first()
        if not exists:
            try:
                db.add(APIKey(key=key))
                db.commit()
                logger.info(f"✅ Added API key: {key}")
            except Exception:
                db.rollback()
                logger.warning(f"⚠️ Skipped duplicate key {key}: (UNIQUE constraint failed)")
        else:
            logger.info(f"🔹 Key already exists: {key}")

    db.close()

def create_app():
    global _initialized

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///alertbot.db')

    CORS(app)
    limiter.init_app(app)

    from app.models import Base
    from app.models import get_engine

    engine = get_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    if not _initialized:
        try:
            safe_init_db(engine, Base)
            init_default_keys()

            from app.queue import start_scheduler
            start_scheduler()
            logger.info("📦 Retry queue scheduler started")
        finally:
            _initialized = True

    from app.routes import register_routes
    register_routes(app)

    try:
        from app.handlers.telegram_handler import setup_telegram_bot, start_telegram_polling
    except Exception:
        setup_telegram_bot = None
        start_telegram_polling = None

    try:
        from app.handlers.facebook_handler import facebook_startup_check, subscribe_page_if_configured, start_facebook_monitor
    except Exception:
        facebook_startup_check = None
        subscribe_page_if_configured = None
        start_facebook_monitor = None

    try:
        if setup_telegram_bot and start_telegram_polling:
            bot_app = setup_telegram_bot()
            if bot_app:
                t = threading.Thread(target=start_telegram_polling, args=(bot_app,), daemon=True)
                t.start()
                logger.info("🤖 Telegram polling started in background thread")
            else:
                logger.info("⚠️ TELEGRAM_BOT_TOKEN not set; Telegram polling not started")
        else:
            logger.debug("🤖 Telegram starter not available; skipping Telegram startup")
    except Exception:
        logger.exception("❌ Failed to initialize Telegram polling")

    try:
        if facebook_startup_check:
            fb_status = facebook_startup_check()
            if fb_status.get("ok"):
                logger.info(f"📡 Facebook token valid: {fb_status.get('details')}")
                if subscribe_page_if_configured:
                    sub_res = subscribe_page_if_configured()
                    if sub_res.get("ok"):
                        logger.info("📡 Facebook page subscription succeeded")
                    else:
                        logger.debug(f"📡 Facebook subscribe attempt result: {sub_res.get('details')}")
            else:
                logger.warning(f"⚠️ Facebook startup check failed: {fb_status.get('details')}")

            if start_facebook_monitor:
                try:
                    start_facebook_monitor(interval_seconds=int(os.getenv("FACEBOOK_MONITOR_INTERVAL", "600")))
                    logger.info("📡 Facebook monitor started")
                except Exception:
                    logger.exception("❌ Failed to start Facebook monitor")
        else:
            logger.debug("📡 Facebook startup helpers not available; skipping FB startup checks")
    except Exception:
        logger.exception("❌ Exception during Facebook startup")

    return app
