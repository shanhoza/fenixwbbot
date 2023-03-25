from aiogram import types

from bot.handlers.messages import start as msg
from bot.keyboards.inline import START_BACK_KB, START_KB


async def start(message: types.Message) -> None:
    await message.answer(
        msg.WELCOME,
        reply_markup=START_KB,
    )


async def callback_of_start_command(callback: types.CallbackQuery):
    processes = {
        'vendor_code': _process_vendor_code,
        'vendor_code_plus_keyword': _process_vendor_code_plus_keyword,
        'return_to_start': _return_to_start,
    }

    data = await processes.get(callback.data)()  # type: ignore
    await callback.message.edit_text(**data)  # type: ignore
    await callback.answer()


async def _process_vendor_code():
    return {
        'text': msg.REQUEST_FOR_VENDOR_CODE,
        'reply_markup': START_BACK_KB
    }


async def _process_vendor_code_plus_keyword():
    return {
        'text': msg.REQUEST_FOR_VENDOR_CODE_AND_KEYWORD,
        'reply_markup': START_BACK_KB,
    }


async def _return_to_start():
    return {
        'text': msg.WELCOME,
        'reply_markup': START_KB
    }
