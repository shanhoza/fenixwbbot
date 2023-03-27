from aiogram import Dispatcher

from bot.middlewares.chat_actions import ChatActionMiddleware
from bot.middlewares.db import MongoDBClient


def register_middlwares(dp: Dispatcher):
    MIDDLEWARES = (
        MongoDBClient,
        ChatActionMiddleware,
    )

    for mw in MIDDLEWARES:
        dp.message.middleware.register(mw())
