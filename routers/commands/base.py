from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from texts import start_text, help_text
from .states import Default

router = Router(name=__name__)



@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    await state.clear()
    text = f"""
    Привет, {message.from_user.full_name}.
    {start_text}
    """
    await message.answer(text)


@router.message(Command("help"))
async def handle_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(help_text)
