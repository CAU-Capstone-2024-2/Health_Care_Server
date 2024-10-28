from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv(".env")
DB_USERNAME=os.getenv("DB_USERNAME")
DB_PASSWORD=os.getenv("DB_PASSWORD")
TEMP_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@localhost:3306/"
DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@localhost:3306/capstone"

temp_engine = create_engine(TEMP_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()

def create_database():
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS capstone"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def rollback_to_savepoint(db, savepoint_name="savepoint"):
    db.execute(text(f"ROLLBACK TO SAVEPOINT {savepoint_name}"))
