from sqlalchemy.orm import Mapped, mapped_column
from .engine import Base
from datetime import date


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    expiry_date: Mapped[date]
    is_active: Mapped[bool] = mapped_column(default=True)
    owner: Mapped[str] = mapped_column(nullable=False)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    tunnel_address: Mapped[str] = mapped_column(nullable=True)
    port: Mapped[int] = mapped_column()
    key: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[bool] = mapped_column(default=True)


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tunnel_address: Mapped[str] = mapped_column(nullable=True)
    port: Mapped[int] = mapped_column(default=1194, nullable=False)
    protocol: Mapped[str] = mapped_column(default="tcp", nullable=False)
