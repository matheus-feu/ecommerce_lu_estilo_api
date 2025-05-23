from typing import Optional, Literal

from fastapi_filter.contrib.sqlalchemy import Filter

from src.models.customer import Customer


class CustomerFilter(Filter):
    class Constants(Filter.Constants):
        model = Customer
        ordering_field_name = "email"

    username__like: Optional[str] = None
    email__like: Optional[str] = None
    role: Optional[Literal["admin", "customer", "employee"]] = None
