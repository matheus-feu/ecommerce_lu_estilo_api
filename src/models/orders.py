import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.dialects import postgresql as pg
from sqlmodel import SQLModel, Field, Relationship, Column


class Order(SQLModel, table=True):
    """
    Order model for the database.
    This model represents an order placed by a customer. (N:1 relationship with Customer)
    """
    __tablename__ = "orders"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4)
    )
    total_price: float = Field(default=0.0)
    customer_id: uuid.UUID = Field(foreign_key="customers.uid")
    status: str = Field(sa_column=Column(pg.VARCHAR(length=20), nullable=False))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    customer_id: uuid.UUID = Field(foreign_key="customers.uid")
    customer: Optional["Customer"] = Relationship(back_populates="orders")
    products: List["OrderProduct"] = Relationship(back_populates="order")


class OrderProduct(SQLModel, table=True):
    """
    OrderProduct model for the database.
    This model represents the many-to-many relationship between orders and products.
    (N:M relationship)
    """
    __tablename__ = "order_products"
    product_id: uuid.UUID = Field(foreign_key="products.uid", primary_key=True)
    product: "Product" = Relationship(back_populates="order_products")
    order_id: uuid.UUID = Field(foreign_key="orders.uid", primary_key=True)
    order: "Order" = Relationship(back_populates="products")
    quantity: int = Field(default=1)
