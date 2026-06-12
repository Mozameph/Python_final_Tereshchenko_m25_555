"""Мок-тесты Telegram-обработчиков: fakeredis вместо Redis,
pytest-mock вместо реальной отправки задач в RabbitMQ."""

from app.bot import handlers
from tests.test_jwt_unit import make_token


async def test_token_command_saves_token_to_redis(patched_redis, make_message):
    token = make_token(sub="7")
    message = make_message(f"/token {token}", user_id=111)

    await handlers.cmd_token(message)

    stored = await patched_redis.get("token:111")
    assert stored == token
    assert any("сохранён" in a.lower() for a in message.answers)


async def test_token_command_rejects_invalid_token(patched_redis, make_message):
    message = make_message("/token not-a-real-jwt", user_id=111)

    await handlers.cmd_token(message)

    assert await patched_redis.get("token:111") is None
    assert any("недействителен" in a.lower() or "истёк" in a.lower() for a in message.answers)


async def test_text_without_token_does_not_call_celery(patched_redis, make_message, mocker):
    delay_mock = mocker.patch("app.bot.handlers.llm_request")
    message = make_message("Расскажи про FastAPI", user_id=555)

    await handlers.handle_text(message)

    delay_mock.delay.assert_not_called()
    assert any("нет сохранённого токена" in a.lower() for a in message.answers)


async def test_text_with_valid_token_sends_celery_task(patched_redis, make_message, mocker):
    delay_mock = mocker.patch("app.bot.handlers.llm_request")
    token = make_token(sub="7")
    await patched_redis.set("token:777", token)
    message = make_message("Что такое Celery?", user_id=777, chat_id=999)

    await handlers.handle_text(message)

    delay_mock.delay.assert_called_once_with(999, "Что такое Celery?")
    assert any("запрос принят" in a.lower() for a in message.answers)


async def test_text_with_expired_token_rejected_and_token_removed(patched_redis, make_message, mocker):
    delay_mock = mocker.patch("app.bot.handlers.llm_request")
    expired = make_token(expires_in_minutes=-1)
    await patched_redis.set("token:888", expired)
    message = make_message("Привет", user_id=888)

    await handlers.handle_text(message)

    delay_mock.delay.assert_not_called()
    assert await patched_redis.get("token:888") is None
    assert any("недействителен" in a.lower() or "истёк" in a.lower() for a in message.answers)
