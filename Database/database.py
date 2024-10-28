# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
TEMP_URL = "mysql+mysqlconnector://rocknroll:rocknroll@localhost:3306/"
DATABASE_URL = "mysql+mysqlconnector://rocknroll:rocknroll@localhost:3306/capstone"
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
