# app/__init__.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/database.db")
DB_URI = f"sqlite:///{DB_PATH}"

# SQLAlchemy setup
engine = create_engine(DB_URI, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Import models and create tables."""
    from app.models import user, transaction
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def init_db():
    """Create tables for all models"""
    from app.models import user  # now includes the user model
    from app.models import transaction  # transaction model will come next
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def init_db():
    """Create tables for all models"""
    from app.models import user
    from app.models import transaction
    Base.metadata.create_all(bind=engine)
    print("successfully!")