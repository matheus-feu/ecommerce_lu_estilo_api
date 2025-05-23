from fastapi import APIRouter, BackgroundTasks
from fastapi import Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer
from src.db.database import get_session
from src.schemas.accounts import (
    UserLoginModel,
    SignupResponseModel
)
from src.services.auth import AuthService

auth_router = APIRouter()


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=SignupResponseModel)
async def create_user(
        user_data: UserLoginModel,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_session)
):
    return await AuthService.signup(user_data, background_tasks, session)


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    return await AuthService.login(login_data, session)


@auth_router.get('/logout')
async def revoke_token(token_details=Depends(AccessTokenBearer())):
    return await AuthService.logout(token_details)
