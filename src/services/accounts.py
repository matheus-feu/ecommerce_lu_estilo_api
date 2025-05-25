from datetime import datetime
from datetime import timedelta

from fastapi import BackgroundTasks, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.sentry import send_to_sentry
from src.core.settings import settings
from src.core.mail import send_email
from src.db.database import get_session
from src.exceptions.errors import UserNotFoundError, InvalidTokenError
from src.models.customer import Customer
from src.schemas.accounts import UserCreateModel
from src.schemas.accounts import PasswordResetConfirmModel
from src.utils.utils import (
    create_url_safe_token,
    decode_reset_password_token,
    render_email_template,
    decode_token,
    create_access_token
)
from src.utils.utils import generate_password_hash


class UserService:

    @classmethod
    async def get_user_by_email(cls, email: str, session: AsyncSession):
        """
        Get a user from the database by email.
        """
        try:
            statement = select(Customer).where(Customer.email == email)
            result = await session.execute(statement)
            user = result.scalars().first()
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred: {str(e)}"
            )

    @classmethod
    async def user_exists(cls, email: str, session: AsyncSession):
        """
        Check if a user exists in the database by email.
        """
        user = await cls.get_user_by_email(email, session)
        return True if user is not None else False

    @classmethod
    async def create_user(cls, user: UserCreateModel, session: AsyncSession):
        """
        Create a new user in the database.
        """
        user_dict = user.model_dump()
        new_user = Customer(**user_dict)

        new_user.password_hash = generate_password_hash(user_dict["password"])
        new_user.role = "customer"
        new_user.is_active = True
        new_user.is_superuser = False
        new_user.created_at = datetime.now()

        session.add(new_user)
        await session.commit()

        return new_user

    @classmethod
    async def update_user(cls, user: Customer, user_data: dict, session: AsyncSession):
        """
        Update an existing user in the database.
        """
        for k, v in user_data.items():
            if hasattr(user, k):
                setattr(user, k, v)

        user.updated_at = datetime.now()
        await session.commit()

        return user


class AccountService:

    @classmethod
    async def verify_email(cls, token: str, session: AsyncSession):
        """
        Verify the email of the user using the token.
        """
        try:
            info = decode_reset_password_token(token=token)
            if info is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token"
                )

            email = info["email"]
            if email:
                user = await UserService.get_user_by_email(email=email, session=session)
                if not user:
                    raise UserNotFoundError()

                await UserService.update_user(user, {"is_verified": True}, session)

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": "Email verified successfully",
                        "success": True,
                        "status_code": status.HTTP_200_OK
                    }
                )
            raise UserNotFoundError()

        except UserNotFoundError:
            raise UserNotFoundError("User not found.")
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def refresh_token(cls, token_details: dict):
        """
        Refresh the access token using the refresh token.
        """
        try:
            token_data = decode_token(token_details.credentials)
            if not token_data:
                raise InvalidTokenError("Token inválido ou malformado")

            expiry_timestamp = token_data["exp"]
            if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
                new_access_token = create_access_token(
                    user_data=token_data,
                    expiry=timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
                )
                return JSONResponse(content={"access_token": new_access_token})

            raise InvalidTokenError("Refresh token expirado")

        except InvalidTokenError:
            raise InvalidTokenError("Token inválido ou malformado")
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def password_reset_request(
            cls,
            email: str,
            background_tasks:
            BackgroundTasks,
            session: AsyncSession
    ):
        """
        Request a password reset link for the user.
        """
        try:
            user = await UserService.get_user_by_email(email=email, session=session)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            access_token = create_url_safe_token({"email": email})
            forget_url_link = (
                f"{settings.app.APP_PROTOCOL}://{settings.app.APP_HOST}:{settings.app.APP_PORT}"
                f"{settings.app.APP_V1_PREFIX}/auth/{settings.auth.FORGET_PASSWORD_URL}?token={access_token}"
            )

            email_body = {
                "company_name": settings.email.MAIL_FROM_NAME,
                "link_expiry_min": settings.auth.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
                "reset_link": forget_url_link
            }
            template_str = """
                Olá {{ company_name }},
                Clique no link para redefinir sua senha: {{ reset_link }}
                O link expira em {{ link_expiry_min }} minutos.
                """

            email_body_str = render_email_template(template_str, email_body)
            background_tasks.add_task(
                send_email,
                email=email,
                subject="Password Reset Request",
                template_body=email_body_str
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Email has been sent", "success": True, "status_code": status.HTTP_200_OK}
            )

        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail
            )
        except Exception as e:
            send_to_sentry(e)

    @classmethod
    async def reset_account_password(
            cls,
            token: str,
            password_data: PasswordResetConfirmModel,
            session: AsyncSession = Depends(get_session)
    ):
        try:
            info = decode_reset_password_token(token=token)
            if info is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token"
                )
            if password_data.new_password != password_data.confirm_new_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords do not match"
                )

            email = info["email"]
            if email:
                user = await UserService.get_user_by_email(email=email, session=session)
                if not user:
                    raise UserNotFoundError()

                hashed_password = generate_password_hash(password_data.new_password)
                user.password_hash = hashed_password
                await UserService.update_user(user, {"password_hash": hashed_password}, session)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Password reset successfully", "success": True, "status_code": status.HTTP_200_OK}
            )

        except UserNotFoundError:
            raise UserNotFoundError("User not found.")
        except Exception as e:
            send_to_sentry(e)
