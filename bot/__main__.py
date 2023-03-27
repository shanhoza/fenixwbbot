import asyncio
import logging

import uvloop
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import bot.config as config
from bot.handlers.user.start import start
from bot.middlewares import register_middlwares

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def __on_startup(dp: Dispatcher) -> None:
    register_middlwares(dp)
    dp.include_router(start.router)


async def start_bot():
    bot = Bot(token=config.API_TOKEN, parse_mode='HTML')  # type: ignore
    dp = Dispatcher(storage=MemoryStorage())
    await __on_startup(dp)

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(start_bot())
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
