import uuid
from datetime import datetime
from typing import List, Optional

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, Column, Relationship

from src.models.category import ProductCategory
from src.models.orders import OrderProduct


class Product(SQLModel, table=True):
    """
    Product model for the database.
    This model represents a product in the store.
    """

    __tablename__ = "products"
    uid: uuid.UUID = Field(primary_key=True, default=uuid.uuid4)
    title: str
    description: str
    price: float
    stock: int
    brand: str
    bar_code: str = Field(
        sa_column=Column(pg.VARCHAR(length=100), nullable=False, unique=True)
    )
    section: str = Field(
        sa_column=Column(pg.VARCHAR(length=100), nullable=False, unique=True)
    )
    date_validation: Optional[datetime] = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True)
    )
    discount_percentage: float = Field(default=0.0)
    rating: float = Field(default=0.0)
    is_published: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, default=False)
    )
    images: List[str] = Field(
        sa_column=Column(JSONB, nullable=False, default=list), default_factory=list
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    order_products: List["OrderProduct"] = Relationship(back_populates="product")
    categories: List["ProductCategory"] = Relationship(back_populates="product")
