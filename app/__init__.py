from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import threading
from sqlalchemy import inspect
import sqlalchemy
from sqlalchemy import create_engine
from flask_limiter.util import get_remote_address

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

_initialized = False


def safe_init_db(engine, Base):
    """
    Create only missing tables in a way that's robust to multiple processes
    (e.g. multiple gunicorn workers) racing to create the same tables.

    Approach:
    - Inspect existing tables first and only attempt to create missing tables.
    - Wrap create_all in a try/except that tolerates SQLite 'table already exists'
      errors which can occur when two processes concurrently decide to create the
      same table after both saw it missing.
    - If a concurrent creation happens, re-check and continue if all tables now exist.
    """
    from sqlalchemy.exc import OperationalError
    inspector = inspect(engine)
    try:
        existing_tables = inspector.get_table_names()
    except Exception:
        # In case inspector fails for whatever reason, fall back to attempting create_all
        existing_tables = []

    missing = [t.name for t in Base.metadata.sorted_tables if t.name not in existing_tables]

    if not missing:
        print("✅ All tables already exist — skipping creation.")
        return

    print(f"🧱 Creating missing tables: {missing}")

    try:
        # checkfirst True is default for create_all, but being explicit
        Base.metadata.create_all(engine, checkfirst=True)
    except OperationalError as e:
        msg = str(e).lower()
        if "already exists" in msg and "table" in msg:
            # Another process likely created the table(s) concurrently.
            print("⚠️ Detected concurrent table creation (another worker created tables). Re-checking...")
            inspector = inspect(engine)
            try:
                existing_tables_after = inspector.get_table_names()
            except Exception:
                existing_tables_after = []

            still_missing = [t.name for t in Base.metadata.sorted_tables if t.name not in existing_tables_after]
            if still_missing:
                # Try once more; if it fails, let the exception propagate.
                try:
                    Base.metadata.create_all(engine, checkfirst=True)
                except Exception:
                    print("❌ Retry failed while creating missing tables. Raising exception.")
                    raise
            else:
                print("✅ All tables exist after concurrent creation — continuing.")
        else:
            # Re-raise unexpected OperationalErrors
            raise


def init_default_keys():
    """Initialize default API keys from app/models key.txt file if present."""
    from app.models import get_session, APIKey
    db = get_session()

    if not os.path.exists('key.txt'):
        print("🔑 key.txt not found — skipping default keys initialization.")
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
                print(f"✅ Added API key: {key}")
            except sqlalchemy.exc.IntegrityError:
                db.rollback()
                print(f"⚠️ Skipped duplicate key {key}: (UNIQUE constraint failed)")
        else:
            print(f"🔹 Key already exists: {key}")

    db.close()


def create_app():
    global _initialized

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///alertbot.db')

    CORS(app)
    limiter.init_app(app)

    # Import DB models and Base
    from app.models import Base  # noqa: E402
    from app.models import get_engine  # get_engine should create engine from config

    engine = get_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    # Safe DB init — guard with an in-process flag to avoid repeated work per worker
    # Note: this flag only prevents multiple in-process initialization. In multi-process
    # environments (gunicorn with multiple workers) safe_init_db is written to tolerate races.
    if not _initialized:
        try:
            safe_init_db(engine, Base)
            init_default_keys()
        finally:
            _initialized = True

    # Register blueprints / routes
    from app.routes import register_routes  # noqa: E402
    register_routes(app)

    return app
