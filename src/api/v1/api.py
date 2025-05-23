from fastapi import APIRouter

from src.api.v1.routers import auth, accounts, customer, products

api_router = APIRouter()

api_router.include_router(auth.auth_router, prefix="/api/v1/auth", tags=["auth"])
api_router.include_router(accounts.accounts_router, prefix="/api/v1/accounts", tags=["accounts"])
api_router.include_router(customer.customers_router, prefix="/api/v1/customers", tags=["customers"])
api_router.include_router(products.products_router, prefix="/api/v1/products", tags=["products"])

# api_router.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
# api_router.include_router(products.router, prefix="/api/v1/products", tags=["products"])
