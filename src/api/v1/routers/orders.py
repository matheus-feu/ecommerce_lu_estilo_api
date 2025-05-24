from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import RoleChecker
from src.db.database import get_session
from src.filters.orders import OrderFilter
from src.schemas.orders import (
    OrderResponseModel,
    OrderBaseModel,
    OrderCreateModel,
    OrderUpdateModel
)
from src.services.orders import OrderService

role_checker = RoleChecker(["admin", "customer"])
orders_router = APIRouter(
    # dependencies=[Depends(role_checker)],
)


@orders_router.get("/", response_model=Page[OrderBaseModel], status_code=status.HTTP_200_OK)
async def list_orders(
        session: AsyncSession = Depends(get_session),
        order_filter: OrderFilter = FilterDepends(OrderFilter),
):
    """
    Listar produtos com filtros e paginação.
    """
    return await OrderService.list_orders(session, order_filter)


@orders_router.post(
    "/", response_model=OrderResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_order(
        order: OrderCreateModel, session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo pedido para o cliente informado,
    valida o estoque dos produtos solicitados e retorna os detalhes do pedido criado.
    """
    return await OrderService.create_order(session, order)


@orders_router.get(
    "/{order_id}", response_model=OrderBaseModel, status_code=status.HTTP_200_OK
)
async def get_order(order_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obter pedido por ID.
    """
    return await OrderService.get_order(session, order_id)


@orders_router.put(
    "/{order_id}", response_model=OrderBaseModel, status_code=status.HTTP_200_OK
)
async def update_order(
        order_id: UUID,
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
async def delete_order(order_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Excluir pedido.
    """
    await OrderService.delete_order(session, order_id)
