from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv(".env")
DB_USERNAME=os.getenv("DB_USERNAME")
DB_PASSWORD=os.getenv("DB_PASSWORD");DB_HOST=os.getenv("DB_HOST")
DB_HOST=os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
TEMP_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:3306/"
DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

temp_engine = create_engine(TEMP_URL)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # 기본값은 5
    max_overflow=20,  # 기본값은 10
    pool_timeout=30,  # 기본값은 30초
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_database():
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS capstone"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def rollback_to_savepoint(db, savepoint_name="savepoint"):
    db.execute(text(f"ROLLBACK TO SAVEPOINT {savepoint_name}"))
