from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import RoleChecker
from src.db.database import get_session
from src.filters.products import ProductFilter
from src.schemas.products import (
    ProductOutModel,
    ProductCreateModel,
    ProductUpdateModel,
    ProductBaseModel
)
from src.services.products import ProductService

role_checker = RoleChecker(["admin", "customer"])

products_router = APIRouter(
    dependencies=[Depends(role_checker)],
)


@products_router.get("/", response_model=Page[ProductBaseModel], status_code=status.HTTP_200_OK)
async def list_products(
        session: AsyncSession = Depends(get_session),
        product_filter: ProductFilter = FilterDepends(ProductFilter),
):
    """
    Listar produtos com filtros e paginação.
    """
    return await ProductService.list_products(session, product_filter)


@products_router.post(
    "/", response_model=ProductOutModel, status_code=status.HTTP_201_CREATED
)
async def create_product(
        product_data: ProductCreateModel, session: AsyncSession = Depends(get_session)
):
    """
    Criar novo produto.
    """
    return await ProductService.create_product(session, product_data)


@products_router.get(
    "/{product_id}", response_model=ProductOutModel, status_code=status.HTTP_200_OK
)
async def get_product(product_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obter produto por ID.
    """
    return await ProductService.get_product(session, product_id)


@products_router.put(
    "/{product_id}", response_model=ProductOutModel, status_code=status.HTTP_200_OK
)
async def update_product(
        product_id: int,
        product: ProductUpdateModel,
        session: AsyncSession = Depends(get_session)
):
    """
    Atualizar produto.
    """
    return await ProductService.update_product(session, product_id, product)


@products_router.delete(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(product_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Excluir produto.
    """
    await ProductService.delete_product(session, product_id)
