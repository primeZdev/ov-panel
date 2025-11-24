from pydantic import BaseModel, Field
from datetime import date
from typing import Any, Optional


class ResponseModel(BaseModel):
    success: bool
    msg: str
    data: Optional[Any] = None


class Users(BaseModel):
    name: str
    is_active: bool
    expiry_date: date
    owner: str
    uuid: str

    class Config:
        from_attributes = True


class ServerInfo(BaseModel):
    cpu: float
    memory_total: int
    memory_used: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    uptime: int

    class Config:
        from_attributes = True


class Settings(BaseModel):
    subscription_url_prefix: Optional[str] = Field(
        None, alias="SUBSCRIPTION_URL_PREFIX"
    )
    subscription_path: Optional[str] = Field("sub", alias="SUBSCRIPTION_PATH")


class Admins(BaseModel):
    username: str

    class Config:
        from_attributes = True
