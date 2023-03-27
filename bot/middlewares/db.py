from typing import Any, Awaitable, Callable

import motor.motor_asyncio
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

import bot.config as cfg
from bot.utils.dbconnect import Request


class MongoDBClient(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        cluster = motor.motor_asyncio.AsyncIOMotorClient(
            'mongodb+srv://{}:{}@{}'.format(
                cfg.MONGO_USERNAME,
                cfg.MONGO_PASSWORD,
                cfg.MONGO_HOST
            )
        )
        data['request'] = Request(cluster)  # type: ignore
        return await handler(event, data)
