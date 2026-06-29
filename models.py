# File: backend/models.py
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, JSON
from datetime import datetime

class Restaurant(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False)
    address: str

    # Direct String References prevent early execution compilation crashes
    dishes: List["Dish"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")
    materials: List["MaterialRequirement"] = Relationship(back_populates="restaurant")

class AddOn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    price: float = Field(nullable=False)

class Dish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: str = Field(foreign_key="restaurant.id")
    name: str = Field(nullable=False)
    description: str
    img: str = Field(default="🥞")
    ingredients: str
    nutrition_content: str
    price: float = Field(nullable=False)
    discount_price: Optional[float] = None
    is_available: bool = Field(default=True)
    addon_ids: List[int] = Field(default=[], sa_type=JSON)

    restaurant: Optional[Restaurant] = Relationship(back_populates="dishes")

class MaterialRequirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: str = Field(foreign_key="restaurant.id")
    material_name: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional[Restaurant] = Relationship(back_populates="materials")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    phone: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="user")
    assigned_restaurant_id: Optional[str] = Field(default=None, foreign_key="restaurant.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryAddress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    flat_no: str = Field(nullable=False)
    area_street: str = Field(nullable=False)
    landmark: Optional[str] = None
    city: str = Field(default="Bengaluru")
    pincode: str = Field(nullable=False, max_length=6)

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: str = Field(foreign_key="restaurant.id")
    user_id: int = Field(foreign_key="user.id")
    dish_name: str = Field(nullable=False)
    addons_selected: Optional[str] = Field(default="None")
    flat_no: str
    area_street: str
    landmark: Optional[str]
    pincode: str
    total_price: float = Field(nullable=False)
    payment_method: str = Field(default="COD")
    status: str = Field(default="Pending")
    delivery_time: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    restaurant: Optional[Restaurant] = Relationship(back_populates="orders")