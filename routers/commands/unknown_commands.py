from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router(name=__name__)

@router.message()
async def handle_all_message(message: Message):
    await message.answer(
        f"""
        Неизвестная команда, введите команду /help для получения списка доступных команд.
        """
    )

@router.callback_query()
async def handle_all_callback(callback: CallbackQuery):
    await callback.answer(
        "Оставьте кнопку в покое (пожалуйста)"
    )