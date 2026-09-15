import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Uses a local SQLite database by default so the Alpha can run without XAMPP.
# To use MySQL instead, set DATABASE_URL in your local .env/environment.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./capstone_group_8.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
