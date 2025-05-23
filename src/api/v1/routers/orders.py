from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_session
from src.schemas.orders import (
    OrderModel,
    OrderCreateModel,
    OrderUpdateModel
)
from src.services.orders import OrderService

orders_router = APIRouter(prefix="/orders", tags=["orders"])


@orders_router.get("/", response_model=List[OrderModel])
async def list_orders(
        session: AsyncSession = Depends(get_session),
        periodo_inicio: Optional[date] = Query(None),
        periodo_fim: Optional[date] = Query(None),
        secao: Optional[str] = Query(None),
        id_pedido: Optional[int] = Query(None),
        status_pedido: Optional[str] = Query(None),
        cliente_id: Optional[int] = Query(None),
        limit: int = Query(10, ge=1),
        offset: int = Query(0, ge=0)
):
    """
    Listar pedidos com filtros e paginação.
    """
    return await OrderService.list_orders(
        session, periodo_inicio, periodo_fim, secao, id_pedido, status_pedido, cliente_id, limit, offset
    )


@orders_router.post(
    "/", response_model=OrderModel, status_code=status.HTTP_201_CREATED
)
async def create_order(
        order: OrderCreateModel, session: AsyncSession = Depends(get_session)
):
    """
    Criar novo pedido, validando estoque.
    """
    return await OrderService.create_order(session, order)


@orders_router.get(
    "/{order_id}", response_model=OrderModel, status_code=status.HTTP_200_OK
)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """
    Obter pedido por ID.
    """
    return await OrderService.get_order(session, order_id)


@orders_router.put(
    "/{order_id}", response_model=OrderModel, status_code=status.HTTP_200_OK
)
async def update_order(
        order_id: int,
        order: OrderUpdateModel,
        session: AsyncSession = Depends(get_session)
):
    """
    Atualizar pedido (incluindo status).
    """
    return await OrderService.update_order(session, order_id, order)


@orders_router.delete(
    "/{order_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """
    Excluir pedido.
    """
    await OrderService.delete_order(session, order_id)
