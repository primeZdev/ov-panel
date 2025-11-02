import os
from pydantic_settings import BaseSettings
from typing import Optional


class Setting(BaseSettings):
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    URLPATH: str = "dashboard"
    HOST: str = "0.0.0.0"
    PORT: int = 9000
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEBUG: str = "WARNING"
    DOC: bool = False
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")


config = Setting()
