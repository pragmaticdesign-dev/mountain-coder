from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database file location (mapped to local folder via Docker)
DATABASE_URL = "sqlite:///./data/mountain.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()