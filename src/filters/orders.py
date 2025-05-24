from datetime import date
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from src.models.orders import Order, OrderStatusEnum


class OrderFilter(Filter):
    class Constants(Filter.Constants):
        model = Order
        ordering_field_name = "created_at"

    uid: Optional[str] = None
    customer_id: Optional[int] = None
    order_id: Optional[int] = None
    status: Optional[OrderStatusEnum] = None
    section: Optional[str] = None
    created_at__ge: Optional[date] = None
    created_at__le: Optional[date] = None

    def apply_filters(self, query):
        if hasattr(self, "status") and self.status:
            query = query.filter(Order.status == self.status)
        return query
