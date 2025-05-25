from uuid import UUID

from fastapi_pagination import paginate
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.core.sentry import send_to_sentry
from src.exceptions.errors import (
    ProductAlreadyExistsError,
    CategoryNotFoundError,
)
from src.models.category import Category, ProductCategory
from src.models.product import Product
from src.schemas.categories import CategoryBaseModel
from src.schemas.products import (
    ProductCreateModel,
    ProductUpdateModel,
    ProductOutModel,
    ProductBaseModel
)


class ProductService:
    """
    Service class for handling product-related operations.
    """

    @classmethod
    async def list_products(cls, session: AsyncSession, product_filter):
        try:
            query = select(Product).options(
                selectinload(Product.categories).selectinload(ProductCategory.category)
            )
            query = product_filter.filter(query)
            result = await session.execute(query)
            products = result.scalars().unique().all()

            products_out: list = []
            for prod in products:
                categories = [
                    CategoryBaseModel(uid=cat.category.uid, name=cat.category.name)
                    for cat in prod.categories
                ]
                prod_dict = prod.model_dump(exclude={"categories"})
                prod_dict["categories"] = categories
                product_out = ProductBaseModel(**prod_dict)
                products_out.append(product_out)

            return paginate(products_out)

        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def create_product(cls, session, product_data: ProductCreateModel):
        try:
            # 1. Verifica se o produto já existe pelo bar_code
            query = await session.execute(
                select(Product).where(Product.bar_code == product_data.bar_code)
            )
            existing_bar_code_product = query.scalar_one_or_none()
            if existing_bar_code_product:
                raise ProductAlreadyExistsError("Product with this bar code already exists.")

            # 2. Separa os UIDs e nomes das categorias
            category_uids = [cat.uid for cat in product_data.categories if cat.uid]
            category_names = [cat.name for cat in product_data.categories if cat.name]

            if not category_uids and not category_names:
                raise CategoryNotFoundError("At least one category UID or name must be provided.")

            # 3. Busca as categorias no banco de dados
            result = await session.execute(
                select(Category).where(
                    or_(
                        Category.uid.in_(category_uids),
                        Category.name.in_(category_names)
                    )
                )
            )
            found_categories = result.scalars().all()
            if len(found_categories) != len(product_data.categories):
                raise CategoryNotFoundError("One or more categories were not found.")

            # 4. Cria o produto e associa as categorias
            product_dict = product_data.model_dump(exclude={"categories"})
            db_product = Product(**product_dict)
            db_product.categories = [
                ProductCategory(product=db_product, category=cat) for cat in found_categories
            ]

            session.add(db_product)
            await session.commit()
            await session.refresh(db_product)

            # 5. Carrega as categorias associadas para evitar o problema de lazy loading
            await session.refresh(db_product, attribute_names=["categories"])

            #  6. Monta a resposta serializável
            categories_out = [
                CategoryBaseModel(uid=cat.category.uid, name=cat.category.name)
                for cat in db_product.categories
            ]
            product_out = ProductBaseModel(**db_product.model_dump(exclude={"categories"}), categories=categories_out)

            return {
                "message": "Successful product",
                "status": "success",
                "data": product_out
            }

        except ProductAlreadyExistsError as e:
            raise ProductAlreadyExistsError(message=str(e))
        except CategoryNotFoundError as e:
            raise CategoryNotFoundError(message=str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def get_product(cls, session: AsyncSession, product_id: UUID):
        try:
            result = await session.execute(
                select(Product)
                .options(selectinload(Product.categories).selectinload(ProductCategory.category))
                .where(Product.uid == product_id)
            )
            product = result.scalar_one_or_none()
            if not product:
                raise NoResultFound("Produto não encontrado")

            return ProductOutModel(
                message="Produto encontrado com sucesso.",
                status="success",
                data=ProductBaseModel(
                    **product.model_dump(exclude={"categories"}),
                    categories=[
                        CategoryBaseModel(uid=cat.category.uid, name=cat.category.name)
                        for cat in product.categories
                    ]
                )
            )

        except NoResultFound as e:
            raise NoResultFound(message=str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def update_product(cls, session: AsyncSession, product_id: UUID, product_data: ProductUpdateModel):
        try:
            result = await session.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()

            if not product:
                raise NoResultFound("Produto não encontrado")
            for key, value in product_data.model_dump(exclude_unset=True).items():
                setattr(product, key, value)

            session.add(product)
            await session.commit()
            await session.refresh(product)

            return {
                "message": "Product updated successfully",
                "status": "success",
                "data": product
            }
        except NoResultFound as e:
            raise NoResultFound(message=str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def delete_product(cls, session: AsyncSession, product_id: UUID):
        try:
            result = await session.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()
            if not product:
                raise NoResultFound("Produto não encontrado")
            await session.delete(product)
            await session.commit()
            return {
                "message": "Product deleted successfully",
                "status": "success",
                "data": product
            }
        except NoResultFound as e:
            raise NoResultFound(message=str(e))
        except Exception as e:
            send_to_sentry(e)
