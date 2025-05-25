import logging

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AppSettings(BaseSettings):
    APP_HOST: str
    APP_V1_PREFIX: str
    APP_PROTOCOL: str = "http"
    APP_PORT: int


class AuthSettings(BaseSettings):
    FORGET_PASSWORD_URL: str
    FORGET_PASSWORD_SECRET_KEY: str
    VERIFICATION_LINK_EXPIRE_MINUTES: int
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRY: int
    REFRESH_TOKEN_EXPIRY: int


class ProductionDBSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str


class SecuritySettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str


class WhatsAppSettings(BaseSettings):
    API_TOKEN: str
    API_PHONE_ID: str
    API_TEMPLATE_NAME: str
    API_TEMPLATE_LANGUAGE: str
    WEBHOOK_TOKEN: str
    WEBHOOK_BASE_URL: str


class LoggingSettings(BaseSettings):
    LOGS_DIR: str = ".logs"
    LOGGING_LEVEL: int = logging.WARNING


class RedisSettings(BaseSettings):
    JTI_EXPIRY: int
    REDIS_URL: str = "redis://localhost:6379/0"


class SentrySettings(BaseSettings):
    SENTRY_DSN: str


class MQTTSettings(BaseSettings):
    MQTT_HOST: str
    MQTT_PORT: int
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_TOPIC: str


class EmailSettings(BaseSettings):
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


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    db: ProductionDBSettings = ProductionDBSettings()
    security: SecuritySettings = SecuritySettings()
    whatsapp: WhatsAppSettings = WhatsAppSettings()
    redis: RedisSettings = RedisSettings()
    mqtt: MQTTSettings = MQTTSettings()
    email: EmailSettings = EmailSettings()
    logs: LoggingSettings = LoggingSettings()
    sentry: SentrySettings = SentrySettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
