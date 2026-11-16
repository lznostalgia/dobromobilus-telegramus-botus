import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DATABASE_URL

from db.database import Database

from tgbot.handlers.user import router as user_router
from tgbot.handlers.admin import router as admin_router


async def main():
    db = Database(DATABASE_URL)
    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(user_router)
    dp.include_router(admin_router)

    try:
        await db.create_tables()

        await dp.start_polling(bot, db=db)

    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())