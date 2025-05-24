from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AddressModel(BaseModel):
    id: UUID
    customer_id: UUID
    address_type: str
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    number: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AddressCreateModel(BaseModel):
    address_type: str
    street: str
    number: int
    city: str
    state: str
    country: str
    postal_code: str
