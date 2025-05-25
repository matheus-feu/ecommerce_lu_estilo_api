from uuid import UUID

from fastapi_pagination import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.core.sentry import send_to_sentry
from src.exceptions.errors import ErrorResponse, ProductNotFoundError
from src.filters.orders import OrderFilter
from src.models.address import Address
from src.models.customer import Customer
from src.models.orders import Order, OrderProduct
from src.models.product import Product
from src.schemas.orders import OrderResponseModel, OrderBaseModel, OrderCreateModel


class OrderService:
    @classmethod
    async def list_orders(cls, session: AsyncSession, order_filter: OrderFilter):
        """
        Listar pedidos com filtros e paginação.
        """
        try:
            query = select(Order).options(selectinload(Order.products))
            query = order_filter.apply_filters(query)
            result = await session.execute(query)
            orders = result.scalars().all()
            return paginate(orders)

        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def create_order(cls, session: AsyncSession, order_data: OrderCreateModel):
        try:
            customer = await session.get(Customer, order_data.customer_id)
            if not customer:
                raise ErrorResponse("Cliente não encontrado.")

            address = await session.get(Address, order_data.shipping_address.id)
            if not address or address.customer_id != order_data.customer_id:
                raise ErrorResponse("Endereço inválido ou não pertence ao cliente.")

            # 1. Obter todos os products_ids do pedido
            products_uids = [item.product_id for item in order_data.items]

            # 2. Consulta todos os produtos envolvidos
            products = await session.execute(
                select(Product).where(Product.uid.in_(products_uids))
            )
            products = products.scalars().all()

            products_map = {product.uid: product for product in products}
            if len(products_map) != len(products_uids):
                raise ProductNotFoundError("Um ou mais produtos não foram encontrados.")

            # 3. Mapeia as quantidades solicitadas
            product_quantities = {item.product_id: item.quantity for item in order_data.items}

            # 4. Valida o estoque de cada produto
            insufficient = [
                product for pid, product in products_map.items()
                if product.stock < product_quantities[pid]
            ]
            if insufficient:
                names = ", ".join([p.name for p in insufficient])
                raise ErrorResponse(f"Estoque insuficiente para: {names}")

            # 5. Debita o estoque
            for pid, product in products_map.items():
                product.stock -= product_quantities[pid]
                session.add(product)

            # 6. Cria o pedido e associa produtos e endereço
            new_order = Order(
                customer_id=order_data.customer_id,
                status=order_data.status,
                shipping_address_id=address.id,
            )
            order_products = [
                OrderProduct(
                    order_id=new_order.uid,
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                for item in order_data.items
            ]
            new_order.products = order_products

            # 7. Salva o pedido
            session.add(new_order)
            await session.commit()
            await session.refresh(new_order)

            await session.refresh(new_order, attribute_names=["products"])

            return OrderResponseModel(
                status="success",
                message="Pedido criado com sucesso.",
                data=OrderBaseModel.from_orm_with_items(new_order)
            )

        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def get_order(cls, session: AsyncSession, order_id: UUID):
        """
        Obter pedido por ID.
        """
        try:
            result = await session.execute(
                select(Order)
                .options(selectinload(Order.products))
                .where(Order.uid == order_id)
            )
            order = result.scalar_one_or_none()
            if not order:
                raise ErrorResponse("Pedido não encontrado.")

            return OrderBaseModel.from_orm_with_items(order)

        except Exception as e:
            send_to_sentry(e)
