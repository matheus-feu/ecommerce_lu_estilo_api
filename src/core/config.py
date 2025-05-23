from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    APP_HOST: str
    APP_V1_PREFIX: str
    APP_PROTOCOL: str = "http"
    APP_PORT: int

    """Authentication settings"""
    FORGET_PASSWORD_URL: str
    FORGET_PASSWORD_SECRET_KEY: str
    VERIFICATION_LINK_EXPIRE_MINUTES: int
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRY: int
    REFRESH_TOKEN_EXPIRY: int

    """Database settings"""
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    """Security settings"""
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    """WhatsApp settings"""
    API_TOKEN: str
    API_PHONE_ID: str
    API_TEMPLATE_NAME: str
    API_TEMPLATE_LANGUAGE: str
    WEBHOOK_TOKEN: str
    WEBHOOK_BASE_URL: str

    """Redis settings"""
    JTI_EXPIRY: int
    REDIS_URL: str = "redis://localhost:6379/0"

    """MQTT settings"""
    MQTT_HOST: str
    MQTT_PORT: int
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_TOPIC: str

    """Email settings"""
    DOMAIN: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
