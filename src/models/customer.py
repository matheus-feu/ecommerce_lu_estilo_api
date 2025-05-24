import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship

from src.models.address import Address
from src.models.orders import Order


class Customer(SQLModel, table=True):
    """
    Customer model for the database.
    """

    __tablename__ = "customers"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: Optional[str] = Field(default=None, nullable=True, max_length=50)
    email: str = Field(nullable=False, unique=True, max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    role: str = Field(default="customer", nullable=False, max_length=20)
    password_hash: str = Field(nullable=False, max_length=255)
    cpf: Optional[str] = Field(default=None, max_length=14)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    orders: List["Order"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    addresses: List["Address"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )