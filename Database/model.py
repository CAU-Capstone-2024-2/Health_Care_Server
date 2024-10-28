import random
import uuid
from sqlalchemy import JSON, DateTime, ForeignKey, Column, Index, Integer, PrimaryKeyConstraint, String, Time, Boolean, UniqueConstraint, event
from sqlalchemy.orm import relationship
from Database.database import Base, db, engine, get_db
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

class Chat(BaseEntity):
    __tablename__ = "chat"
    id = Column(Integer, index = True, autoincrement = True, primary_key = True)
    uid = Column(String(255), index=True)
    isuser = Column(Boolean)
    utterance = Column(String(600))