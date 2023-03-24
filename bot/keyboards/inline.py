from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

START_KB = InlineKeyboardMarkup(inline_keyboard=[
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

START_BACK_KB = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Назад',
            callback_data='return_to_start'
        )
    ]
])
