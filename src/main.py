#Standard libraries
import asyncio
import logging

#Telegram
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

#Modules
import config
#import database
#import handlers



#Below is a sample configuration from https://aiogram.dev/

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.full_name}!")


@dp.message()
async def echo(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def main(token=None) -> None:
    """
    Main function to spool things up.
    Attempts to read a Telegram bot token:
        * optionally from function argument (debug),
        * or from the environment.
    """
    if token == None:
        token = config.get_bot_token()

    bot = Bot()
    await dp.start_polling(bot)

    #TODO

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())