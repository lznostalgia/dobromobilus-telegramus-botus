from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        f"Добро пожаловать в приют, {message.from_user.full_name}!"
    )

