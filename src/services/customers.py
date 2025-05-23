from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.exceptions.errors import UserNotFound
from src.models.customer import Customer
from src.schemas.customers import (
    CustomerModel,
    CustomerCreateModel,
    CustomerUpdateModel
)
from src.utils.utils import generate_password_hash


class CustomerService:

    @classmethod
    async def get_customer(cls, session: AsyncSession, customer_id: int):
        try:
            query = select(Customer).where(Customer.uid == customer_id)
            result = await session.execute(query)
            customer = result.scalar_one_or_none()
            if not customer:
                raise UserNotFound(f"Cliente com ID {customer_id} não encontrado.")

            return {
                "message": "Cliente encontrado com sucesso",
                "status": "success",
                "data": CustomerModel.model_validate(customer)
            }

        except UserNotFound as e:
            return JSONResponse(
                content={
                    "message": str(e),
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

    @classmethod
    async def create_customer(cls, session: AsyncSession, costumer: CustomerCreateModel):
        try:
            query = select(Customer).where(
                (Customer.email == costumer.email) | (Customer.cpf == costumer.cpf)
            )
            result = await session.execute(query)
            existing_customer = result.scalar_one_or_none()
            if existing_customer:
                return JSONResponse(
                    content={
                        "message": "Cliente já existe com esse email ou CPF",
                        "status": "error"
                    },
                    status_code=status.HTTP_409_CONFLICT
                )

            hashed_password = generate_password_hash(costumer.password)
            customer_data = costumer.dict(exclude={"password"})
            customer_data["password_hash"] = hashed_password

            db_customer = Customer(**customer_data)
            session.add(db_customer)
            await session.commit()
            await session.refresh(db_customer)

            return {
                "message": "Cliente criado com sucesso",
                "status": "success",
                "data": [CustomerModel.model_validate(db_customer)]
            }

        except Exception as e:
            return JSONResponse(
                content={
                    "message": f"Erro ao criar cliente: {str(e)}",
                    "status": "error"
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @classmethod
    async def update_customer(cls, session: AsyncSession, customer_id: int, update_customer: CustomerUpdateModel):
        try:
            query = select(Customer).where(Customer.uid == customer_id)
            result = await session.execute(query)
            db_customer = result.scalar_one_or_none()
            if not db_customer:
                raise UserNotFound(f"Cliente com ID {customer_id} não encontrado.")

            if update_customer.password:
                hashed_password = generate_password_hash(update_customer.password)
                db_customer.password_hash = hashed_password

            for key, value in update_customer.dict(exclude_unset=True, exclude={"password"}).items():
                if hasattr(db_customer, key):
                    setattr(db_customer, key, value)

            await session.commit()
            await session.refresh(db_customer)

            return {
                "message": "Cliente atualizado com sucesso",
                "status": "success",
                "data": CustomerModel.model_validate(db_customer)
            }

        except UserNotFound as e:
            return JSONResponse(
                content={
                    "message": str(e),
                    "status": "error"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

    @classmethod
    async def delete_customer(cls, session: AsyncSession, customer_id: int):
        try:
            query = select(Customer).where(Customer.uid == customer_id)
            result = await session.execute(query)
            db_customer = result.scalar_one_or_none()
            if not db_customer:
                raise UserNotFound(f"Cliente com ID {customer_id} não encontrado.")

            await session.delete(db_customer)
            await session.commit()

            return {
                "message": "Cliente atualizado com sucesso",
                "status": "success",
                "data": CustomerModel.model_validate(db_customer).model_dump()
            }

        except UserNotFound as e:
            return JSONResponse(
                content={
                    "message": str(e),
                    "status": "error"
                },
                status_code=status.HTTP_404_NOT_FOUND
            )
