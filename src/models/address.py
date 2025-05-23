import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Field, SQLModel, Relationship, Column


class Address(SQLModel, table=True):
    """
    Address model for the database.
    """
    __tablename__ = "addresses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.uid")
    address_type: str
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    customer: Optional["Customer"] = Relationship(back_populates="addresses")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
