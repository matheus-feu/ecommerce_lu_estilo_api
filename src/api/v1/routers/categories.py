from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.auth.security import RoleChecker
from src.db.database import get_session
from src.exceptions.errors import ErrorResponse
from src.filters.categories import CategoryFilter
from src.models.category import Category
from src.schemas.categories import (
    CategoryBaseModel,
    CategoryOutModel,
    CategoryCreateModel,
    CategoryUpdateModel,
    CategoryOutDeleteModel
)
from src.services.categories import CategoryService

role_checker = RoleChecker(["admin", "customer"])
categories_router = APIRouter(
    dependencies=[Depends(role_checker)],
)


@categories_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoryBaseModel],
)
async def get_all_categories(
        session: AsyncSession = Depends(get_session),
        category_filter: CategoryFilter = FilterDepends(CategoryFilter),
):
    """
    Get all categories with optional filters.
    :param session:
    :param category_filter:
    :return:
    """
    try:
        query = select(Category)
        query = category_filter.filter(query)
        result = await session.execute(query)
        categories = result.scalars().unique().all()
        return paginate(categories)
    except Exception as e:
        raise ErrorResponse(message=str(e))


@categories_router.get(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryOutModel
)
async def get_category(category_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Get a category by its ID.
    :param category_id:
    :param session:
    :return:
    """
    return await CategoryService.get_category(session, category_id)


@categories_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryOutModel,
)
async def create_category(category: CategoryCreateModel, session: AsyncSession = Depends(get_session)):
    """
    Create a new category.
    :param category:
    :param session:
    :return:
    """
    return await CategoryService.create_category(session, category)


@categories_router.put(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryOutModel
)
async def update_category(
        category_id: UUID,
        updated_category: CategoryUpdateModel,
        session: AsyncSession = Depends(get_session)
):
    """
    Update an existing category.
    :param category_id:
    :param updated_category:
    :param session:
    :return:
    """
    return await CategoryService.update_category(session, category_id, updated_category)


@categories_router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryOutDeleteModel
)
async def delete_category(category_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Delete a category by its ID.
    :param category_id:
    :param session:
    :return:
    """
    return await CategoryService.delete_category(session, category_id)
