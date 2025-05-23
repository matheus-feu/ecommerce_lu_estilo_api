from datetime import timedelta

from fastapi import BackgroundTasks
from fastapi import status
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.mail import send_email
from src.db.redis import add_jti_to_blocklist
from src.exceptions.errors import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidToken
)
from src.schemas.accounts import SignupResponseModel, UserResponseModel
from src.services.accounts import UserService
from src.utils.utils import (
    create_access_token,
    verify_password,
    create_url_safe_token,
    render_email_template,
    decode_token
)


class AuthService:

    @classmethod
    async def signup(cls, user_data, background_tasks: BackgroundTasks, session):
        """
        Cria um novo cliente e envia e-mail de verificação.
        """
        try:
            email = user_data.email
            if await UserService.user_exists(email=email, session=session):
                raise UserAlreadyExists()

            token = create_url_safe_token({"email": email})

            new_user = await UserService.create_user(user_data, session)
            verification_url = f"{settings.APP_PROTOCOL}://{settings.APP_HOST}:{settings.APP_PORT}{settings.APP_V1_PREFIX}/accounts/verify-email?token={token}"

            email_body = {
                "company_name": settings.MAIL_FROM_NAME,
                "link_expiry_min": settings.VERIFICATION_LINK_EXPIRE_MINUTES,
                "verification_link": verification_url
            }
            template_str = """
                Olá {{ company_name }},
                Clique no link para verificar seu e-mail: {{ verification_link }}
                O link expira em {{ link_expiry_min }} minutos.
                """

            email_body_str = render_email_template(template_str, email_body)
            background_tasks.add_task(
                send_email,
                email=email,
                subject="Email Verification",
                template_body=email_body_str
            )
            return SignupResponseModel(
                user=UserResponseModel.model_validate(new_user),
                success=True,
                status_code=status.HTTP_201_CREATED,
                message="User created successfully. Please check your email for verification.",
            )

        except Exception as e:
            raise UserAlreadyExists("User with this email already exists: {}".format(e))

    @classmethod
    async def login(cls, login_data, session):
        """
        Login a user and return access and refresh tokens.
        """
        try:
            email = login_data.email
            password = login_data.password
            user = await UserService.get_user_by_email(email=email, session=session)

            if not user or not verify_password(password, user.password_hash):
                raise InvalidCredentials()

            if not getattr(user, "is_verified", False):
                raise InvalidCredentials()

            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(getattr(user, "uid", None)),
                    "role": user.role
                }
            )
            refresh_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(getattr(user, "uid", None)),
                    "role": user.role
                },
                refresh=True,
                expiry=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            )

            return JSONResponse(
                content={
                    "role": user.role,
                    "user_uid": str(getattr(user, "uid", None)),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status_code=status.HTTP_200_OK
            )

        except UserAlreadyExists:
            raise UserAlreadyExists("User with this email already exists.")
        except InvalidCredentials:
            raise InvalidCredentials("Account not verified. Please check your email to verify your account.")
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")

    @classmethod
    async def logout(cls, token_details):
        """
        Logout a user by adding the token to the blocklist.
        """
        try:
            token_data = decode_token(token_details.credentials)
            if not token_data:
                raise InvalidToken("Token inválido")

            jti = token_data["jti"]
            await add_jti_to_blocklist(jti)

            return JSONResponse(content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK)
        except Exception:
            raise InvalidToken("Token inválido ou malformado")
