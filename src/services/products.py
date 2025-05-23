from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select

from src.exceptions.errors import (
    ProductCreateError,

from src.models.product import Product
from src.schemas.products import ProductCreateModel, ProductUpdateModel


class ProductService:
    """
    Service class for handling product-related operations.
    """

    @classmethod
    async def create_product(cls, session, product_data: ProductCreateModel):
        try:
            db_product = Product(**product_data.model_dump())
            session.add(db_product)
            await session.commit()
            await session.refresh(db_product)
            return db_product
        except Exception as e:
            raise ProductCreateError(f"Erro ao criar produto: {e}")

    @staticmethod
    async def get_product(session, product_id: int):
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise NoResultFound("Produto não encontrado")
        return product

    @staticmethod
    async def update_product(session, product_id: int, product_data: ProductUpdateModel):
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise NoResultFound("Produto não encontrado")
        for key, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    @staticmethod
    async def delete_product(session, product_id: int):
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise NoResultFound("Produto não encontrado")
        await session.delete(product)
        await session.commit()
