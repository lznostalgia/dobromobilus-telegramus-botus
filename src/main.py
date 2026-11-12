#Standard libraries
import asyncio
import logging

#Telegram
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

#Modules
from config import BOT_TOKEN
#from db.database import Database
from tgbot.handlers.sample import router

async def main() -> None:
    #db = Database()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    #Yoink
    try:
        await dp.start_polling(bot)

    finally:
        """await db.close()""" # REMOVE BEFORE FLIGHT
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())