import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import API_TOKEN
from bot.database.models import register_models
from bot.handlers import register_user_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def __on_startup(dp: Dispatcher) -> None:
    # register_admin_handlers(dp)
    await register_user_handlers(dp)
    # register_models(dpAPI_TOKEN=None)


async def start_bot():
    bot = Bot(token=API_TOKEN, parse_mode='HTML')  # type: ignore
    dp = Dispatcher()  # , storage=MemoryStorage())

    dp.startup.register(__on_startup)

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        # close_db()
        pass
