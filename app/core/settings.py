import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

ENV: str = "test"


class Settings(BaseSettings):
    PROJECT_NAME: str = "MV Tracking Hub"
    API_VERSION: str = os.getenv("API_VERSION", "0.0.1")
    ENV: str = os.getenv("ENV", ENV)
    API: str = "/api"
    API_V1_STR: str = "/api/v1"

    # date
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (
        60 * 24 * 7
    )  # 60 minutes * 24 hours * 7 days = 7 days
    AUTH_ALGORITHM: str = os.getenv("AUTH_ALGORITHM", "HS256")
    VERIFY_TOKEN_EXPIRE_DAYS: int = os.getenv("VERIFY_TOKEN_EXPIRE_DAYS", 3)
    PASSWORD_RESET_TOKEN_EXPIRE_DAYS: int = os.getenv(
        "PASSWORD_RESET_TOKEN_EXPIRE_DAYS", 3
    )

    # database
    DB_USER: str = os.getenv("DB_USER", "mvi_tracking_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "mvi_tracking_pass")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "mvi_tracking_db")
    DB_ENGINE: str = os.getenv("DB", "postgresql")

    DATABASE_URI: str = (
        "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
            db_engine=DB_ENGINE,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
        )
    )

    # Graylog
    GRAYLOG_HOST: str = os.getenv("GRAYLOG_HOST", "localhost")
    GRAYLOG_PORT: int = os.getenv("GRAYLOG_PORT", 12201)

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # mailing
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "live.smtp.mailtrap.io")
    MAIL_PORT: int = os.getenv("MAIL_PORT", 587)
    MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", True)
    MAIL_USE_SSL: bool = os.getenv("MAIL_USE_SSL", False)
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_SUBJECT: str = os.getenv("MAIL_SUBJECT", "MVI tracking email verification")
    PASSWORD_RESET_MAIL_SUBJECT: str = os.getenv(
        "PASSWORD_RESET_MAIL_SUBJECT", "MVI tracking password reset"
    )

    MAIL_VERIFICATION_MESSAGE: str = os.getenv(
        "MAIL_VERIFICATION_MESSAGE",
        "Please use the button link below to verify your account and get started with MVI tracking solutions.",
    )

    PASSWORD_RESET_MAIL_VERIFICATION_MESSAGE: str = os.getenv(
        "PASSWORD_RESET_MAIL_VERIFICATION_MESSAGE",
        "Please use the button link below to reset your password",
    )

    # mqtt
    MQTT_HOST: str = os.getenv("MQTT_HOST", "3.98.106.16")
    MQTT_PORT: int = os.getenv("MQTT_PORT", 1883)
    MQTT_TOPIC: str = os.getenv("MQTT_TOPIC", "tracking/istartek")
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "admin")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "public")

    # find query
    PAGE: int = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"

    class Config:
        case_sensitive = True


settings = Settings()


class TestConfigs(Settings):
    ENV: str = "test"


if ENV == "production":
    pass
elif ENV == "staging":
    pass
elif ENV == "test":
    setting = TestConfigs()


@lru_cache
def get_settings():
    return settings
