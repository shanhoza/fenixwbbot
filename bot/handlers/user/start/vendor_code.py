from aiogram import F, Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext

from bot.handlers.messages import start as msg
from bot.handlers.user.start import StartCommandStates
from bot.keyboards.inline import START_BACK_KB

router = Router()


@router.callback_query(Text('vendor_code'))
async def _vendor_code_callback(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await state.set_state(StartCommandStates.waiting_for_vendor_code)
    await callback.message.edit_text(  # type: ignore
        text=msg.REQUEST_FOR_VENDOR_CODE,
        reply_markup=START_BACK_KB
    )


@router.message(StartCommandStates.waiting_for_vendor_code,
                F.text,
                flags={'long_operation': 'typing'})
async def vendor_code_sent(message: types.Message, state: FSMContext):
    await message.answer(text='получен vendor_code')
    await state.clear()
