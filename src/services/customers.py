from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.sentry import send_to_sentry
from src.exceptions.errors import (
    UserNotFoundError,
    CustomerAlreadyExistsError
)
from src.models.address import Address
from src.models.customer import Customer
from src.schemas.customers import (
    CustomerModel,
    CustomerCreateModel,
    CustomerUpdateModel
)
from src.utils.utils import generate_password_hash


class CustomerService:

    @classmethod
    async def get_customer(cls, session: AsyncSession, customer_id: UUID):
        try:
            query = (
                select(Customer)
                .where(Customer.uid == customer_id)
                .options(selectinload(Customer.addresses))
            )
            result = await session.execute(query)
            customer = result.scalar_one_or_none()
            if not customer:
                raise UserNotFoundError(f"Cliente com ID {customer_id} não encontrado.")

            return {
                "message": "Cliente encontrado com sucesso",
                "status": "success",
                "data": CustomerModel.model_validate(customer, from_attributes=True)
            }

        except UserNotFoundError as e:
            raise UserNotFoundError(str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def create_customer(cls, session: AsyncSession, costumer: CustomerCreateModel):
        try:
            query = select(Customer).where(
                (Customer.email == costumer.email) | (Customer.cpf == costumer.cpf)
            )
            result = await session.execute(query)
            existing_customer = result.scalar_one_or_none()
            if existing_customer:
                raise CustomerAlreadyExistsError()

            hashed_password = generate_password_hash(costumer.password)
            customer_data = costumer.dict(exclude={"password"})
            customer_data["password_hash"] = hashed_password

            db_customer = Customer(**customer_data)
            session.add(db_customer)
            await session.flush()

            address_data = costumer.address.dict(exclude_unset=True)
            db_address = Address(**address_data, customer_id=db_customer.uid)
            session.add(db_address)

            await session.commit()
            await session.refresh(db_customer)
            await session.refresh(db_address)

            return {
                "message": "Successful Customer",
                "status": "success",
                "data": [CustomerModel.model_validate(db_customer)]
            }
        except CustomerAlreadyExistsError as e:
            raise CustomerAlreadyExistsError(str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def update_customer(cls, session: AsyncSession, customer_id: int, update_customer: CustomerUpdateModel):
        try:
            query = select(Customer).where(Customer.uid == customer_id)
            result = await session.execute(query)
            db_customer = result.scalar_one_or_none()
            if not db_customer:
                raise UserNotFoundError(f"Cliente com ID {customer_id} não encontrado.")

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

        except UserNotFoundError as e:
            raise UserNotFoundError(str(e))
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def delete_customer(cls, session: AsyncSession, customer_id: int):
        try:
            query = select(Customer).where(Customer.uid == customer_id)
            result = await session.execute(query)
            db_customer = result.scalar_one_or_none()
            if not db_customer:
                raise UserNotFoundError(f"Cliente com ID {customer_id} não encontrado.")

            await session.delete(db_customer)
            await session.commit()

            return {
                "message": "Cliente atualizado com sucesso",
                "status": "success",
                "data": CustomerModel.model_validate(db_customer).model_dump()
            }

        except UserNotFoundError as e:
            raise UserNotFoundError(str(e))
        except Exception as e:
            send_to_sentry(e)
