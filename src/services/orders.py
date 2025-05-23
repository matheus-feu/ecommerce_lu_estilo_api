from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from src.models.products import Product
from src.schemas.orders import OrderCreateModel, OrderUpdateModel

from src.models.orders import Order, OrderProduct

class OrderService:
    @staticmethod
    async def list_orders(session, periodo_inicio, periodo_fim, secao, id_pedido, status_pedido, cliente_id, limit,
                          offset):
        query = select(Order)
        filters = []
        if periodo_inicio:
            filters.append(Order.created_at >= periodo_inicio)
        if periodo_fim:
            filters.append(Order.created_at <= periodo_fim)
        if id_pedido:
            filters.append(Order.id == id_pedido)
        if status_pedido:
            filters.append(Order.status == status_pedido)
        if cliente_id:
            filters.append(Order.cliente_id == cliente_id)
        if secao:
            query = query.join(Order.items).join(OrderProduct.product).where(Product.secao == secao)
        if filters:
            query = query.where(and_(*filters))
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().unique().all()

    @staticmethod
    async def create_order(session, order_data: OrderCreateModel):
        # Validar estoque dos produtos
        for item in order_data.items:
            result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = result.scalar_one_or_none()
            if not product or product.estoque_inicial < item.quantity:
                raise ValueError(f"Estoque insuficiente para o produto {item.product_id}")
        # Criar pedido e itens
        db_order = Order(
            cliente_id=order_data.cliente_id,
            status=order_data.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(db_order)
        await session.flush()
        for item in order_data.items:
            db_item = OrderProduct(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price
            )
            session.add(db_item)
            # Atualizar estoque
            result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = result.scalar_one()
            product.estoque_inicial -= item.quantity
            session.add(product)
        await session.commit()
        await session.refresh(db_order)
        return db_order

    @staticmethod
    async def get_order(session, order_id: int):
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NoResultFound("Pedido não encontrado")
        return order

    @staticmethod
    async def update_order(session, order_id: int, order_data: OrderUpdateModel):
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NoResultFound("Pedido não encontrado")
        for key, value in order_data.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
        order.updated_at = datetime.utcnow()
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @staticmethod
    async def delete_order(session, order_id: int):
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NoResultFound("Pedido não encontrado")
        await session.delete(order)
        await session.commit()
