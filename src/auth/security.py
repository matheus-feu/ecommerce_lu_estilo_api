from typing import List, Any

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer
from src.db.database import get_session
from src.exceptions.errors import InsufficientPermission, AccountNotVerified, InvalidToken, UserNotFound
from src.models.customer import Customer
from src.services.accounts import UserService


async def get_current_user(
        token_details: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session),
):
    try:
        user_email = token_details.get("email")
        if not user_email:
            raise InvalidToken("Token inválido ou expirado.")

        user = await UserService.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound("Usuário não encontrado.")

        if not user.is_verified:
            raise AccountNotVerified("Usuário não verificado.")

        return user

    except Exception as e:
        raise InvalidToken(f"Token inválido ou expirado: {str(e)}")

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Customer = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
