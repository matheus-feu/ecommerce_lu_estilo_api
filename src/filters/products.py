from typing import Optional
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter

from src.models.product import Product


class ProductFilter(Filter):
    class Constants(Filter.Constants):
        model = Product
        ordering_field_name = "uid"

    titulo__ilike: Optional[str] = None
    preco__ge: Optional[float] = None
    preco__le: Optional[float] = None
    estoque__ge: Optional[int] = None
    is_published: Optional[bool] = None
    categories__name__ilike: Optional[str] = None
    order_products__order_id__eq: Optional[UUID] = None
    order_products__quantity__ge: Optional[int] = None
