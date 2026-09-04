from sqlalchemy import create_engine #in engine.create
from sqlalchemy.orm import sessionmaker #can't find
from sqlalchemy.orm import declarative_base #in decl_api

DATABASE_URL = "mysql+mysqlconnector://mgs_user:pa55word@localhost/capstone_group_8"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
