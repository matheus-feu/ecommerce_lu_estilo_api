import uuid
from typing import List
from typing import TYPE_CHECKING

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Relationship, Column

if TYPE_CHECKING:
    from src.models.product import Product


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(
        sa_column=Column(pg.VARCHAR(length=100), nullable=False, unique=True)
    )
    products: List["ProductCategory"] = Relationship(back_populates="category")


class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_categories"

    product_id: uuid.UUID = Field(foreign_key="products.uid", primary_key=True)
    category_id: uuid.UUID = Field(foreign_key="categories.uid", primary_key=True)
    product: "Product" = Relationship(back_populates="categories")
    category: "Category" = Relationship(back_populates="products")
