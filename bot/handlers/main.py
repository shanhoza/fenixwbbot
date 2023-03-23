from aiogram import Dispatcher

from .user.start import callback_of_start_command, start


async def register_user_handlers(dp: Dispatcher):
    USER_HANDLERS_WITH_CALLBACKS = {
        start: callback_of_start_command
    }

    for handler, callback in USER_HANDLERS_WITH_CALLBACKS.items():
        dp.message.register(handler)
        dp.callback_query.register(callback)
