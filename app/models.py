from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///alertbot.db'))
Session = sessionmaker(bind=engine)


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


def init_db():
    """Safely create only missing tables to prevent 'table already exists' errors."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    for table_name, table_obj in Base.metadata.tables.items():
        if table_name not in existing_tables:
            table_obj.create(engine)


def get_session():
    return Session()
