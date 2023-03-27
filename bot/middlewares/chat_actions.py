from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, types
from aiogram.dispatcher.flags import get_flag
from aiogram.utils.chat_action import ChatActionSender


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message, dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: dict[str, Any]
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # Если такого флага на хэндлере нет
        if not long_operation_type:
            return await handler(event, data)

        # Если флаг есть
        async with ChatActionSender(
            action=long_operation_type,
            chat_id=event.chat.id
        ):
            return await handler(event, data)
