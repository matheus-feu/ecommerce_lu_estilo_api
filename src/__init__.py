from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from src.api.v1.api import api_router
from src.core.logger import logger
from src.core.middleware import register_middleware
from src.core.settings import settings
from src.db.database import async_engine
from src.db.database import init_db
from src.exceptions.errors import register_all_errors

description = """
    Welcome to the Lu Estilo E-commerce API documentation. 🚀

    This API is designed to facilitate the management of our e-commerce platform,

    Key features include:
    - **Crud operations** 
        - for managing products, orders, and clients.
    - **Search functionality**
        - to quickly find products by name or category.
    - **Authentication**
        - to ensure secure access to the API.
    - **Permission management**
        - to control access to different parts of the API.
    - **Validation**
        - to ensure that all data sent to the API is correct and complete.
    - **Error handling**
        - to provide clear and informative error messages.
    - **Documentation**
        - to help you understand how to use the API effectively.

    For any questions or issues, please refer to the documentation or contact our support team.
    We hope you enjoy using our API! 😊

    Please contact us: 
    - Github: https://github.com/matheus-feu
    """


def include_router(app):
    app.include_router(api_router)


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield


app = FastAPI(
    description=description,
    title="Lu Estilo E-commerce API",
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Matheus Feu",
        "url": "https://github.com/matheus-feu"
    },
    openapi_url="/openapi.json",
    redoc_url="/api/v1/redoc",
    docs_url="/api/v1/docs",
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "layout": "BaseLayout",
        "filter": True,
        "tryItOutEnabled": True,
        "onComplete": "Ok"
    },
)

add_pagination(app)
include_router(app)

disable_installed_extensions_check()

register_all_errors(app)
register_middleware(app)


@app.get("/api/v1/healthcheck", tags=["healthcheck"])
async def healthcheck():
    """
    Healthcheck endpoint to verify if the API is running.
    """
    return {"message": "Welcome to the Lu Estilo E-commerce API! 🚀"}
