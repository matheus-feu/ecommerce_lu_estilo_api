from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_pagination import paginate, Page
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.security import RoleChecker
from src.db.database import get_session
from src.filters.customers import CustomerFilter
from src.models.customer import Customer
from src.schemas.customers import (
    CustomerModel,
    CustomerCreateModel,
    CustomerUpdateModel,
    CustomersOutModel,
    CustomerOutModel
)
from src.services.customers import CustomerService

role_checker = RoleChecker(["admin", "customer"])
customers_router = APIRouter(
    dependencies=[Depends(role_checker)],
)


@customers_router.get(
    "/",
    response_model=Page[CustomerModel],
    status_code=status.HTTP_200_OK
)
async def get_all_customers(
        customer_filter: CustomerFilter = FilterDepends(CustomerFilter),
        session: AsyncSession = Depends(get_session),
):
    query = select(Customer)
    query = customer_filter.filter(query)
    result = await session.execute(query)
    customers = result.scalars().unique().all()
    return paginate(customers)


@customers_router.post(
    "/",
    response_model=CustomersOutModel,
    status_code=status.HTTP_201_CREATED
)
async def create_new_customer(customer: CustomerCreateModel, session: AsyncSession = Depends(get_session)):
    """
    Create a new customer.
    :param customer:
    :param session:
    :return:
    """
    return await CustomerService.create_customer(session, customer)


@customers_router.get(
    "/{customer_id}",
    response_model=CustomerOutModel,
    status_code=status.HTTP_200_OK
)
async def get_customer(customer_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Get a customer by ID.
    :param customer_id:
    :param session:
    :return:
    """
    return await CustomerService.get_customer(session, customer_id)


@customers_router.put(
    "/{customer_id}",
    response_model=CustomerOutModel,
    status_code=status.HTTP_200_OK
)
async def update_customer(
        customer_id: UUID,
        customer: CustomerUpdateModel,
        session: AsyncSession = Depends(get_session)
):
    """
    Update a customer.
    :param customer_id:
    :param customer:
    :param session:
    :return:
    """
    return await CustomerService.update_customer(session, customer_id, customer)


@customers_router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(customer_id: UUID, session: AsyncSession = Depends(get_session)):
    await CustomerService.delete_customer(session, customer_id)
