from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class BaseExceptionError(Exception):
    """This is the base class for all exceptions in this module"""

    pass


class InvalidTokenError(BaseExceptionError):
    """User has provided an invalid or expired token"""

    def __init__(self, message="Invalid token"):
        self.message = message
        super().__init__(message)


class AccessTokenRequiredError(BaseExceptionError):
    """User has provided a refresh token when an access token is needed"""

    def __init__(self, message="Access token required"):
        self.message = message
        super().__init__(message)


class RefreshTokenRequiredError(BaseExceptionError):
    """User has provided an access token when a refresh token is needed"""

    def __init__(self, message="Refresh token required"):
        self.message = message
        super().__init__(message)


class AccountNotVerifiedError(BaseExceptionError):
    """User has not verified their account"""

    def __init__(self, message="Account not verified"):
        self.message = message
        super().__init__(message)


class InsufficientPermissionError(BaseExceptionError):
    """User does not have sufficient permissions to perform this action"""

    def __init__(self, message="Insufficient permission"):
        self.message = message
        super().__init__(message)


class UserAlreadyExistsError(BaseExceptionError):
    """User already exists"""

    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(message)


class CustomerAlreadyExistsError(BaseExceptionError):
    """Customer already exists"""

    def __init__(self, message="Customer already exists"):
        self.message = message
        super().__init__(message)


class UserNotFoundError(BaseExceptionError):
    """User not found"""

    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(message)


class InvalidCredentialsError(BaseExceptionError):
    """User has provided invalid credentials"""

    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(message)


class ProductCreateError(BaseExceptionError):
    """Error creating product"""

    def __init__(self, message="Erro ao criar produto"):
        self.message = message
        super().__init__(self.message)


class ProductNotFoundError(BaseExceptionError):
    """Product not found"""

    def __init__(self, message="Product not found"):
        self.message = message
        super().__init__(self.message)


class ProductAlreadyExistsError(BaseExceptionError):
    """Product already exists"""

    def __init__(self, message="Product already exists"):
        self.message = message
        super().__init__(self.message)


class CategoryNotFoundError(BaseExceptionError):
    """Category not found"""

    def __init__(self, message="Category not found"):
        self.message = message
        super().__init__(self.message)


class CategoryAlreadyExistsError(BaseExceptionError):
    """Category already exists"""

    def __init__(self, message="Category already exists"):
        self.message = message
        super().__init__(self.message)


class ErrorResponse(BaseExceptionError):
    """Erro genérico de resposta"""

    def __init__(self, message="Error when processing the request"):
        self.message = message
        super().__init__(self.message)


def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BaseExceptionError):
        detail = initial_detail.copy()
        if hasattr(exc, "message"):
            detail["message"] = exc.message
        detail.setdefault("status", "error")
        detail["status_code"] = status_code
        return JSONResponse(content=detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExistsError, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "User already exists", "error_code": "user_already_exists", }
        ),
    )

    app.add_exception_handler(
        UserNotFoundError, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "User not found", "error_code": "user_not_found", }
        ),
    )

    app.add_exception_handler(
        InvalidCredentialsError, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid credentials", "error_code": "invalid_credentials", }
        ),
    )
    app.add_exception_handler(
        InvalidTokenError, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid token", "error_code": "invalid_token", }
        ),
    )
    app.add_exception_handler(
        AccessTokenRequiredError, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Access token required", "error_code": "access_token_required", }
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequiredError, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Refresh token required", "error_code": "refresh_token_required", }
        ),
    )
    app.add_exception_handler(
        AccountNotVerifiedError, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "Account not verified", "error_code": "account_not_verified", }
        ),
    )
    app.add_exception_handler(
        InsufficientPermissionError, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "Insufficient permission", "error_code": "insufficient_permission", }
        ),
    )
    app.add_exception_handler(
        ErrorResponse, create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={"message": "Erro ao processar a requisição", "error_code": "error_response"}
        ),
    )
    app.add_exception_handler(
        ProductCreateError, create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={"message": "Erro ao criar produto", "error_code": "product_create_error"}
        ),
    )
    app.add_exception_handler(
        CategoryNotFoundError, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "Categoria não encontrada", "error_code": "category_not_found"}
        ),
    )
    app.add_exception_handler(
        CustomerAlreadyExistsError, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "Customer already exists", "error_code": "customer_already_exists"}
        ),
    )
    app.add_exception_handler(
        SQLAlchemyError, create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={"message": "Erro ao processar a requisição", "error_code": "sqlalchemy_error"}
        ),
    )
    app.add_exception_handler(
        IntegrityError, create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={"message": "Erro de integridade", "error_code": "integrity_error"}
        ),
    )
    app.add_exception_handler(
        CategoryAlreadyExistsError, create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={"message": "Category already exists", "error_code": "category_already_exists"}
        ),
    )
    app.add_exception_handler(
        ProductAlreadyExistsError, create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={"message": "Product already exists", "error_code": "product_already_exists"}
        ),
    )
    app.add_exception_handler(
        ProductNotFoundError, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "Product not found", "error_code": "product_not_found"}
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request, exc):
        return JSONResponse(
            content={
                "message": "There is already a record with this unique value.",
                "error_code": "unique_violation",
            },
            status_code=status.HTTP_409_CONFLICT,
        )
