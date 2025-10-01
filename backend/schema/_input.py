from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class CreateUser(BaseModel):
    name: str = Field(min_length=3, max_length=10)
    # traffic: int = Field(default=0, ge=0, le=999) # canceled for now
    expiry_date: date


class UpdateUser(BaseModel):
    expiry_date: Optional[date]


class NodeCreate(BaseModel):
    name: str = Field(max_length=10)
    address: str
    tunnel_address: str = Field(default=None)
    port: int
    key: str = Field(min_length=10, max_length=40)
    status: bool = Field(default=True)


class SettingsUpdate(BaseModel):
    tunnel_address: Optional[str] = None
    port: Optional[int]
    protocol: Optional[str]
