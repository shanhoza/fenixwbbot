#!venv/bin/python
import logging
import logging.config
import redis
import threading
import asyncio
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot.api import TelegramAPIServer
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageNotModified, Throttled, RetryAfter
from aiogram.utils.exceptions import InvalidQueryID

from bot import BotFenix
from config import API_TOKEN, LOGGING
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


bot_instance = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
# bot_instance = Bot(
#   token=BOT_API, parse_mode=types.ParseMode.HTML, server=TelegramAPIServer.from_base('http://localhost:8081')
# )
bot_dispatcher = Dispatcher(bot_instance, storage=MemoryStorage())


# logging.basicConfig(level=logging.INFO)


@bot_dispatcher.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    return True


@bot_dispatcher.errors_handler(exception=RetryAfter)
async def exception_handler(update: types.Update, exception: RetryAfter):
    # print('Exception', exception)
    return True


@bot_dispatcher.errors_handler(exception=InvalidQueryID)
async def exception_handler(update: types.Update, exception: RetryAfter):
    # print('Exception', exception)
    return True


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(__name__)

    redis_storage = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        charset='utf-8',
        decode_responses=True
    )

    # Запустить 1 раз только эту функцию, чтобы разлогиниться с API server-a
    # потом раскомментировать строку с локальным сервером и после поднятия контейнера подключиться
    # asyncio.run(bot_instance.log_out())
    _bot = BotFenix(bot_instance, bot_dispatcher, logger=logger, cache=redis_storage)
    _bot.initialize()

    try:
        while True:
            executor.start_polling(bot_dispatcher, skip_updates=True, on_startup=_bot.on_startup)
            time.sleep(10)
    except KeyboardInterrupt:
        print('Goodbye--Goodbye!')
