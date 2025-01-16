import asyncio
import logging
import cowsay

from bot_config import TOKEN
from aiogram import Bot, Dispatcher
from routers import router as main_router
from database.db import init_db

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(main_router)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        cowsay.trex("рррррр")