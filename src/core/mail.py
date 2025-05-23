from pathlib import Path

from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail, MessageSchema, MessageType

from src.core.config import settings

BASE_DIR = Path(__file__).resolve().parent

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

mail = FastMail(config=mail_conf)


async def send_email(email: str, subject: str, template_body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        template_body=template_body,
        subtype=MessageType.html
    )
    await mail.send_message(message)
