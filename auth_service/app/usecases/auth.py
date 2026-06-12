"""Бизнес-логика Auth Service: register / login / me.

Слой не содержит SQL - только вызовы репозитория и функций безопасности.
"""

from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UsersRepository


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository) -> None:
        self._users = users_repo

    async def register(self, email: str, password: str) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError()
        return await self._users.create(email=email, password_hash=hash_password(password))

    async def login(self, email: str, password: str) -> str:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(sub=user.id, role=user.role)

    async def me(self, user_id: int) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
