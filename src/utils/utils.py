import logging
import uuid
from datetime import timedelta, datetime

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from jinja2 import Template
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from src.core.settings import settings

passwd_context = CryptContext(schemes=["bcrypt"])

serializer = URLSafeTimedSerializer(
    secret_key=settings.security.JWT_SECRET_KEY, salt="email-configuration"
)


def generate_password_hash(password: str) -> str:
    """
    Generate a password hash using bcrypt.
    """
    return passwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    """
    Generates a JSON Web Token (JWT), signed with a predefined secret and algorithm,
    that contains user-specific data and an expiration timestamp. Allows specifying
    whether the token is a refresh token and customizes the expiration duration if desired.

    :param user_data: A dictionary containing information that will be included
        in the payload of the JWT.
    :type user_data: dict

    :param expiry: (Optional) A timedelta object specifying the duration after
        which the token expires. Defaults to 15 minutes if not provided.
    :type expiry: timedelta, optional

    :param refresh: A boolean flag to indicate whether the token is a refresh token.
    :type refresh: bool

    :return: A JWT string containing the provided user data, expiration timestamp,
        and a unique identifier.
    :rtype: str
    """
    if expiry is None:
        expiry = timedelta(minutes=15)

    exp = datetime.now() + expiry
    payload = {
        **user_data,
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        payload,
        key=settings.security.JWT_SECRET_KEY,
        algorithm=settings.security.JWT_ALGORITHM
    )

    return token


def decode_token(token: str):
    try:
        token_data = jwt.decode(
            token,
            settings.security.JWT_SECRET_KEY,
            algorithms=[settings.security.JWT_ALGORITHM]
        )
        return token_data
    except ExpiredSignatureError:
        logging.warning("Token expirado.")
        return None
    except JWTError as e:
        logging.exception(e)
        return None


def create_url_safe_token(data: dict) -> str:
    """
    Cria um token seguro para URL.
    """

    return serializer.dumps(data)


def decode_url_safe_token(token: str, max_age: int = 3600) -> dict | None:
    """
    Decodifica um token seguro de URL.
    """
    try:
        return serializer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired) as e:
        logging.error(f"Token inválido ou expirado: {e}")
        return None


def decode_reset_password_token(token: str) -> str | None:
    """
    Decodifica um token de redefinição de senha.
    """
    try:
        payload = jwt.decode(
            token,
            key=settings.security.JWT_SECRET_KEY,
            algorithms=[settings.security.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        return email
    except jwt.JWTError:
        pass

    try:
        data = decode_url_safe_token(token)
        return data
    except Exception:
        return None


def render_email_template(template_str: str, context: dict) -> str:
    template = Template(template_str)
    return template.render(**context)
