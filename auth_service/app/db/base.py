"""Единый источник Base для всех ORM-моделей сервиса."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
