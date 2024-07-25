import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from myproject import config
from myproject import common, ordering_food


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value())
    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
