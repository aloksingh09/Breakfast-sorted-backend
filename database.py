# File: backend/database.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from models import *

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

def init_db():
    # Force evaluate all relational strings constraints mappings inside registry
    SQLModel.metadata.configure()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session