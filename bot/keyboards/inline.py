from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

START_COMMAND_INLINE_KB = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Артикул',
            callback_data='vendor_code'
        ),
        InlineKeyboardButton(
            text='Артикул + Ключевой запрос',
            callback_data='vendor_code_plus_keyword'
        )
    ]
])
