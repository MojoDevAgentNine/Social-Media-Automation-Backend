import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
load_dotenv()

# URL_DATABASE = 'postgresql://postgres:123456789@localhost:5432/quizapplication'
#
# engine = create_engine(URL_DATABASE)
# Use environment variable for database URL, with a default value for development

DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()