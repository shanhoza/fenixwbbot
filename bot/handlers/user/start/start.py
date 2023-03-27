from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext

from bot.handlers.messages import start as msg
from bot.handlers.user.start import vendor_code, vendor_code_plus_keyword
from bot.keyboards.inline import START_KB
from bot.utils.dbconnect import Request

router = Router()
router.include_routers(
    vendor_code.router,
    vendor_code_plus_keyword.router,
)


@router.message(Command('start'), flags={'long_operation': 'typing'})
async def start(
        message: types.Message,
        request: Request,
        state: FSMContext
) -> None:
    """Main logic for the /start command

    Args:
        message (types.Message): aiogram type of message
        request (Request): custom request class to perform database connections
        state (FSMContext): FSM state changer to handle messages by user
    """
    await state.clear()
    await request.add_user(message.from_user)  # type: ignore
    await message.answer(msg.WELCOME, reply_markup=START_KB)


@router.callback_query(Text('return_to_start'))
async def _return_to_start_callback(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await state.clear()
    await callback.message.edit_text(  # type: ignore
        text=msg.WELCOME,
        reply_markup=START_KB
    )
