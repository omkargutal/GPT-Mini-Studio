# ==========================================
# GPT Mini Studio: Data Models (ORM)
# ==========================================
# This module defines the SQL tables for Users, Sessions, 
# and Messages using SQLAlchemy's Declarative Base.

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

# Represents a user account in the system.
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    credits = Column(Integer, default=50) # 50 credits = 25,000 tokens
    last_credit_refresh = Column(DateTime, default=datetime.datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

'''
# Relationships:
sessions = relationship("ChatSession")

# Structure:
User
 └── ChatSession
       └── Messages
'''

# Represents one conversation thread where Each user can have multiple chat sessions.
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Chat")
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")



# Represents a single user message & Stores each message inside a chat
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" or "model"
    content = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


