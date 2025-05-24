from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.schemas.address import AddressModel


class OrderProductItemModel(BaseModel):
    product_id: UUID
    quantity: int


class OrderProductOutModel(OrderProductItemModel):
   pass


class OrderBaseModel(BaseModel):
    uid: UUID
    total_price: float
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderProductOutModel]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_with_items(cls, order):
        return cls(
            uid=order.uid,
            total_price=order.total_price,
            customer_id=order.customer_id,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderProductOutModel(
                    product_id=op.product_id,
                    quantity=op.quantity
                )
                for op in getattr(order, "products", [])
            ],
        )


class OrderCreateModel(BaseModel):
    customer_id: UUID
    status: str
    items: List[OrderProductItemModel]
    shipping_address: AddressModel

    @field_validator("items")
    def items_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("O pedido deve conter pelo menos um item.")
        return v


class OrderResponseModel(BaseModel):
    status: str
    message: str
    data: OrderBaseModel


class OrderListResponseModel(BaseModel):
    status: str
    message: str
    data: List[OrderBaseModel]


class OrderUpdateModel(BaseModel):
    status: Optional[str] = None
