import random
import uuid
from sqlalchemy import JSON, DateTime, ForeignKey, Column, Index, Integer, PrimaryKeyConstraint, String, Time, Boolean, UniqueConstraint, event
from sqlalchemy.orm import relationship
from Database.database import Base
from datetime import datetime, timezone, timedelta
import hashlib

def hash_id():
    unique_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + str(uuid.uuid4())
    return hashlib.sha256(unique_string.encode()).hexdigest()

class BaseEntity(Base):
    __abstract__ = True
    is_deleted = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.now)
    updated_at = Column(DateTime, default = datetime.now, onupdate = datetime.now)

class User(BaseEntity):
    __tablename__ = "user"
    uid = Column(String(255), index = True, primary_key = True)
    period = Column(Integer, nullable=True)
    form_id = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    disease = Column(String(255), nullable=True)


class BasicChat(BaseEntity):
    __abstract__ = True
    id = Column(Integer, index = True, autoincrement = True, primary_key = True)
    sessionId = Column(String(255), index = True)
    uid = Column(String(255), index=True)
    isuser = Column(Boolean)
    utterance = Column(String(600))
    type = Column(String(10))

class Chat(BasicChat):
    __tablename__ = "chat"

class CompleteChat(BasicChat):
    __tablename__ = "complete_chat"
    def __init__(self, chat: Chat):
        self.sessionId = chat.sessionId
        self.uid = chat.uid
        self.isuser = chat.isuser
        self.utterance = chat.utterance
        self.type = chat.type