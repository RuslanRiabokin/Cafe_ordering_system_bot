import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from myproject import common, ordering_food

# Загружаем переменные окружения из файла .env
load_dotenv()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot_token = os.getenv('BOT_TOKEN')  # Получаем токен из переменных окружения
    bot = Bot(bot_token)
    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
