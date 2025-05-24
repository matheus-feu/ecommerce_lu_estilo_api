from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from src.db.redis import token_in_blocklist
from src.exceptions.errors import (
    InvalidTokenError, AccessTokenRequiredError, RefreshTokenRequiredError,
)
from src.utils.utils import decode_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict | None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials

        token_data = decode_token(token)
        if not self.token_valid(token_data):
            raise InvalidTokenError()

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidTokenError()

        self.verify_token(token_data)

        return token_data

    def token_valid(self, token_data: dict | None) -> bool:
        return token_data is not None

    def verify_token(self, token: str):
        pass


class AccessTokenBearer(JWTBearer):
    """
    Verifies if the token is an access token. Rejects refresh tokens.
    """
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequiredError()
        return None


class RefreshTokenBearer(JWTBearer):
    """
    Verifies if the token is a refresh token. Rejects access tokens.
    """
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequiredError()
        return None
