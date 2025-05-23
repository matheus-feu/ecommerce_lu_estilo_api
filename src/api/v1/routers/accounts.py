from fastapi import APIRouter, BackgroundTasks
from fastapi import Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RefreshTokenBearer
from src.db.database import get_session
from src.schemas.accounts import (
    PasswordResetRequestModel,
    PasswordResetConfirmModel
)
from src.services.accounts import AccountService

accounts_router = APIRouter()


@accounts_router.get('/verify-email')
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    return await AccountService.verify_email(token, session)


@accounts_router.get('/refresh_token')
async def get_new_access_token(token_details=Depends(RefreshTokenBearer())):
    return await AccountService.refresh_token(token_details)


@accounts_router.post('/password-reset/request', status_code=status.HTTP_200_OK)
async def password_reset_request(
        email_data: PasswordResetRequestModel,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_session)
):
    return await AccountService.password_reset_request(email_data.email, background_tasks, session)


@accounts_router.post('/password-reset/confirm')
async def reset_account_password(
    password_data: PasswordResetConfirmModel,
    token: str = Query(..., description="Token de redefinição de senha"),
    session: AsyncSession = Depends(get_session)
):
    return await AccountService.reset_account_password(token, password_data, session)