from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class BaseException(Exception):
    """This is the base class for all exceptions in this module"""

    pass


class InvalidToken(BaseException):
    """User has provided an invalid or expired token"""

    def __init__(self, message="Invalid token"):
        self.message = message
        super().__init__(message)


class AccessTokenRequired(BaseException):
    """User has provided a refresh token when an access token is needed"""

    def __init__(self, message="Access token required"):
        self.message = message
        super().__init__(message)


class RefreshTokenRequired(BaseException):
    """User has provided an access token when a refresh token is needed"""

    def __init__(self, message="Refresh token required"):
        self.message = message
        super().__init__(message)


class AccountNotVerified(BaseException):
    """User has not verified their account"""

    def __init__(self, message="Account not verified"):
        self.message = message
        super().__init__(message)


class InsufficientPermission(BaseException):
    """User does not have sufficient permissions to perform this action"""

    def __init__(self, message="Insufficient permission"):
        self.message = message
        super().__init__(message)


class UserAlreadyExists(BaseException):
    """User already exists"""

    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(message)


class UserNotFound(BaseException):
    """User not found"""

    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(message)


class InvalidCredentials(BaseException):
    """User has provided invalid credentials"""

    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(message)


class ProductCreateError(Exception):
    def __init__(self, message="Erro ao criar produto"):
        self.message = message
        super().__init__(self.message)


def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BaseException):
        detail = initial_detail.copy()
        if hasattr(exc, "message"):
            detail["message"] = exc.message
        return JSONResponse(content=detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "User already exists", "error_code": "user_already_exists", }
        ),
    )

    app.add_exception_handler(
        UserNotFound, create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "User not found", "error_code": "user_not_found", }
        ),
    )

    app.add_exception_handler(
        InvalidCredentials, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid credentials", "error_code": "invalid_credentials", }
        ),
    )
    app.add_exception_handler(
        InvalidToken, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid token", "error_code": "invalid_token", }
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Access token required", "error_code": "access_token_required", }
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired, create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Refresh token required", "error_code": "refresh_token_required", }
        ),
    )
    app.add_exception_handler(
        AccountNotVerified, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "Account not verified", "error_code": "account_not_verified", }
        ),
    )
    app.add_exception_handler(
        InsufficientPermission, create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "Insufficient permission", "error_code": "insufficient_permission", }
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
