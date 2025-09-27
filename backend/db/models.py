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
    port: Mapped[int] = mapped_column()
    status: Mapped[bool] = mapped_column(default=True)
