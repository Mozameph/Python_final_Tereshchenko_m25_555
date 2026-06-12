"""Обработчики Telegram-бота.

Логика авторизации: пользователь получает JWT в Auth Service и передаёт
его командой /token <jwt>. Токен валидируется и сохраняется в Redis под
ключом token:<tg_user_id>. Обычный текст обрабатывается ТОЛЬКО при
наличии валидного токена и уходит в Celery (llm_request.delay) —
напрямую к LLM из хэндлера запросы не выполняются.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.core.jwt import TokenValidationError, decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()

NO_TOKEN_TEXT = (
    "У вас нет сохранённого токена доступа.\n\n"
    "1. Зарегистрируйтесь и войдите в Auth Service (Swagger: http://localhost:8000/docs)\n"
    "2. Скопируйте access_token\n"
    "3. Отправьте мне команду: /token <ваш_jwt>"
)

INVALID_TOKEN_TEXT = (
    "Токен недействителен или истёк. Получите новый токен в Auth Service "
    "(POST /auth/login) и отправьте его командой /token <jwt>."
)

REQUEST_ACCEPTED_TEXT = "Запрос принят! Готовлю ответ, это может занять немного времени..."


def token_key(tg_user_id: int) -> str:
    return f"token:{tg_user_id}"


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот LLM-консультаций.\n\n"
        "Доступ только по JWT-токену, выданному Auth Service.\n"
        "Авторизуйтесь: /token <jwt>, затем просто пришлите свой вопрос."
    )


@router.message(Command("token"))
async def cmd_token(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Использование: /token <jwt>")
        return

    token = parts[1].strip()
    try:
        payload = decode_and_validate(token)
    except TokenValidationError:
        await message.answer(INVALID_TOKEN_TEXT)
        return

    redis = get_redis()
    await redis.set(token_key(message.from_user.id), token)
    await message.answer(
        f"Токен сохранён. Вы авторизованы как пользователь id={payload['sub']} "
        f"(role={payload.get('role', 'user')}). Теперь просто пришлите вопрос."
    )


@router.message(F.text)
async def handle_text(message: Message) -> None:
    redis = get_redis()
    token = await redis.get(token_key(message.from_user.id))

    if not token:
        await message.answer(NO_TOKEN_TEXT)
        return

    try:
        decode_and_validate(token)
    except TokenValidationError:
        await redis.delete(token_key(message.from_user.id))
        await message.answer(INVALID_TOKEN_TEXT)
        return

    # Публикуем задачу в RabbitMQ; обработает Celery worker
    llm_request.delay(message.chat.id, message.text)
    await message.answer(REQUEST_ACCEPTED_TEXT)
