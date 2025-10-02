import os
from pydantic_settings import BaseSettings
from typing import Optional


class Setting(BaseSettings):
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    URLPATH: str = "dashboard"
    PORT: int = 9000
    DEBUG: str = "WARNING"
    DOCS: Optional[str] = None
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")


config = Setting()
