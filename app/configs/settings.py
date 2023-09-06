import os

from pydantic_settings import BaseSettings
from functools import lru_cache

class SharedSettings(BaseSettings):
    app_name: str = "MV Tracking Hub"
    app_version: str = "0.0.1"
    database_uri: str = ""

class DevSettings(SharedSettings):
    pass

class ProdSettings(SharedSettings):
    pass

@lru_cache()
def get_settings():
    app_env = os.getenv("MVTRACK_ENVIRONMENT", "")
    if app_env is None:
        return DevSettings()