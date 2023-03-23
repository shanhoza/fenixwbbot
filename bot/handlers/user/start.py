from aiogram import types

from bot.handlers.messages import start as msg
from bot.keyboards.inline import START_COMMAND_INLINE_KB


async def start(message: types.Message) -> None:
    await message.answer(
        msg.WELCOME,
        reply_markup=START_COMMAND_INLINE_KB,
    )


async def callback_of_start_command(callback: types.CallbackQuery):
    processes = {
        'vendor_code': _process_vendor_code,
        'vendor_code_plus_keyword': _process_vendor_code_plus_keyword,
    }
    answer_text, result = await processes[callback.data]()  # type: ignore

    await callback.message.edit_text(answer_text)  # type: ignore


async def _process_vendor_code():
    return msg.REQUEST_FOR_VENDOR_CODE, 1


async def _process_vendor_code_plus_keyword():
    return msg.REQUEST_FOR_VENDOR_CODE_AND_KEYWORD, 1
