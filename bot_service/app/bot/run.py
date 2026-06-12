"""Entrypoint Telegram-бота."""

import asyncio
import logging

from app.bot.dispatcher import create_bot, create_dispatcher

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = create_bot()
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
