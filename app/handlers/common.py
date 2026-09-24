from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.support import category_keyboard

router = Router(name="common")


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Здравствуйте! Выберите тему обращения:",
        reply_markup=category_keyboard(),
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Нажмите /start, выберите категорию и отправьте обращение одним сообщением."
    )