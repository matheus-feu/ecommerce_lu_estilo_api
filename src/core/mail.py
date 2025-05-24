from pathlib import Path

from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail, MessageSchema, MessageType

from src.core.settings import settings

BASE_DIR = Path(__file__).resolve().parent

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.email.MAIL_USERNAME,
    MAIL_PASSWORD=settings.email.MAIL_PASSWORD,
    MAIL_FROM=settings.email.MAIL_FROM,
    MAIL_PORT=settings.email.MAIL_PORT,
    MAIL_SERVER=settings.email.MAIL_SERVER,
    MAIL_FROM_NAME=settings.email.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.email.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.email.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.email.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.email.VALIDATE_CERTS
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
