from aiogram import Dispatcher

from .user.start import callback_of_start_command, start


async def register_user_handlers(dp: Dispatcher):
    USER_HANDLERS = {
        # add user handlers by adding a function and the callback that function refers
        start: callback_of_start_command,
    }

    for handler, callback in USER_HANDLERS.items():
        dp.message.register(handler)
        dp.callback_query.register(callback)
