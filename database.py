# File: backend/database.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Force load all cross-references compile checks
from models import Restaurant, Dish, AddOn, Order, MaterialRequirement, User, DeliveryAddress

def init_db():
    # Force evaluate all relational strings constraints mappings inside registry
    SQLModel.metadata.configure()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session