# ==========================================
# GPT Mini Studio: Database Connectivity
# ==========================================
# This module sets up the SQLite database connection using SQLAlchemy.
# It defines the 'engine' and 'get_db' dependency for FastAPI routes.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Using SQLite for local development, storing data in "app.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Setting "check_same_thread": False is required for SQLite and FastAPI concurrent connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# sessions for queries (insert, select, update, delete).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables matching our defined models
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
