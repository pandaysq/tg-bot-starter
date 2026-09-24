import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import Settings
from app.database.engine import create_database
from app.handlers import admin, common, support


async def main() -> None:
    settings = Settings()
    database = create_database(settings.database_url)
    await database.create_schema()

    bot = Bot(token=settings.bot_token.get_secret_value())
    dispatcher = Dispatcher()
    dispatcher["database"] = database
    dispatcher["settings"] = settings
    dispatcher.include_routers(common.router, support.router, admin.router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await database.dispose()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(main())