from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import os

# Base declaration
Base = declarative_base()

# Engine & session setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///alertbot.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = scoped_session(sessionmaker(bind=engine))

# ---------------------------
# Models
# ---------------------------

class APIKey(Base):
    __tablename__ = 'api_keys'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class MessageLog(Base):
    __tablename__ = 'message_logs'
    id = Column(Integer, primary_key=True)
    channel = Column(String(20), nullable=False)
    recipient = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    retry_count = Column(Integer, default=0)


class RetryQueue(Base):
    __tablename__ = 'retry_queue'
    id = Column(Integer, primary_key=True)
    channel = Column(String(20), nullable=False)
    recipient = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    attempts = Column(Integer, default=0)
    next_retry = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------------------
# Database Utility Functions
# ---------------------------
def init_db():
    """Safely create only missing tables."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    for table_name, table_obj in Base.metadata.tables.items():
        if table_name not in existing_tables:
            table_obj.create(engine)


def get_engine(db_url: str | None = None):
    """
    Return an engine for the given db_url. If db_url is None or matches the
    module DATABASE_URL, return the module-level engine.
    """
    if db_url is None or db_url == DATABASE_URL:
        return engine
    connect_args = {"check_same_thread": False} if 'sqlite' in db_url else {}
    return create_engine(db_url, connect_args=connect_args)


def get_session(engine_arg=None):
    """Get a session. If engine_arg is provided, return a session bound to it,
    otherwise return the module-scoped SessionLocal().
    """
    if engine_arg is None:
        return SessionLocal()
    Session = sessionmaker(bind=engine_arg)
    return Session()
