from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.sentry import send_to_sentry
from src.exceptions.errors import (
    ErrorResponse,
    CategoryNotFoundError,
    CategoryAlreadyExistsError
)
from src.models.category import Category
from src.schemas.categories import CategoryCreateModel


class CategoryService:

    @classmethod
    async def get_category(cls, session: AsyncSession, category_id: int):
        try:
            result = await session.execute(
                select(Category).where(Category.uid == category_id)
            )
            db_category = result.scalar_one_or_none()
            if not db_category:
                raise CategoryNotFoundError()

            return {
                "message": "Category retrieved successfully",
                "status": "success",
                "data": db_category,
            }

        except CategoryNotFoundError as e:
            raise CategoryNotFoundError(message=str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def create_category(cls, session: AsyncSession, category_data: CategoryCreateModel):
        result = await session.execute(
            select(Category).where(Category.name == category_data.name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise CategoryAlreadyExistsError()
        try:
            db_category = Category(**category_data.model_dump())
            session.add(db_category)
            await session.commit()
            await session.refresh(db_category)

            return {
                "message": "Category created successfully",
                "status": "success",
                "data": db_category,
            }
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def update_category(cls, session: AsyncSession, category_id: int, updated_category):
        try:
            result = await session.execute(
                select(Category).where(Category.uid == category_id)
            )
            db_category = result.scalar_one_or_none()
            if not db_category:
                raise CategoryNotFoundError()

            for key, value in updated_category.model_dump(exclude_unset=True).items():
                setattr(db_category, key, value)

            session.add(db_category)
            await session.commit()
            await session.refresh(db_category)

            return {
                "message": "Category updated successfully",
                "status": "success",
                "data": db_category,
            }
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def delete_category(cls, session: AsyncSession, category_id: int):
        try:
            result = await session.execute(
                select(Category).where(Category.uid == category_id)
            )
            db_category = result.scalar_one_or_none()
            if not db_category:
                raise CategoryNotFoundError()

            await session.delete(db_category)
            await session.commit()

            return {
                "status": "success",
                "message": "Category deleted successfully",
                "data": db_category
            }

        except Exception as e:
            send_to_sentry(e)
