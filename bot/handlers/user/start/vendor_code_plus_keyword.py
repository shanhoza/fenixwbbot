import asyncio
import time

import aiohttp
import orjson
from aiogram import F, Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext

from bot import config
from bot.handlers.messages import start as msg
from bot.handlers.user.start import StartCommandStates
from bot.keyboards.inline import START_BACK_KB

router = Router()


@router.callback_query(Text('vendor_code_plus_keyword'))
async def _vendor_code_plus_keyword_callback(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await state.set_state(StartCommandStates.waiting_for_vendor_code_and_keyword)
    await callback.message.edit_text(  # type: ignore
        text=msg.REQUEST_FOR_VENDOR_CODE_AND_KEYWORD,
        reply_markup=START_BACK_KB
    )


@router.message(StartCommandStates.waiting_for_vendor_code_and_keyword,
                F.text,
                flags={'long_operation': 'typing'})
async def vendor_code_and_keyword_sent(
        message: types.Message,
        state: FSMContext
):
    await parse_wb_api(message.text.lower(), state)  # type: ignore
    answer = _prepare_answer(await state.get_data())
    await message.answer(text=answer)
    await state.clear()


async def parse_wb_api(user_query: str, state: FSMContext):
    if user_query.find(' '):
        vendor_code, search_query = user_query.split(maxsplit=1)
    else:
        vendor_code, search_query = user_query, None

    async with (
        aiohttp.ClientSession() as session,
        asyncio.TaskGroup() as tg,
    ):
        for city_name, city_query in config.WB_API_CITIES_QUERIES.items():
            for page in range(0, config.WB_API_NUMBER_OF_PAGES_TO_PARSE + 1):
                tg.create_task(
                    _get_wb_api_data(
                        session=session,
                        city_query=city_query,
                        page=page,
                        search_query=search_query,
                        vendor_code=int(vendor_code),
                        city_name=city_name,
                        state=state,
                    )
                )


async def _get_wb_api_data(
        session: aiohttp.ClientSession,
        city_query: str,
        page: int,
        search_query: str | None,
        vendor_code: int,
        city_name: str,
        state: FSMContext,
) -> None:

    url = config.WB_API_URL.format(city_query, page, search_query)
    async with session.get(url) as response:
        # todo write to mongo
        try:
            data = orjson.loads(await response.text())
            products = data['data']['products']
        except (KeyError, orjson.JSONDecodeError):
            return

        position = _get_position(products, vendor_code)
        if position:
            await _write_wb_data_to_state(
                position,
                page,
                search_query,
                vendor_code,
                city_name,
                state,
            )


def _prepare_answer(data: dict[str, list[str | int]]):
    if not data:
        return "Товар или артикул не найден"
    start_string = "Ваш товар находится на\n"
    end_string = "\nПоиск выполняется без учета рекламных мест на странице"
    cities_strings = [
        f'🌐{city}:\n     🖥 стр.{data[2]} поз.{data[3]}'
        for city, data in data.items()
    ]
    cities_strings.sort()
    return '{}{}{}'.format(start_string, '\n'.join(cities_strings), end_string)


async def _write_wb_data_to_state(
    position: int,
    page: int,
    search_query: str | None,
    vendor_code: int,
    city_name: str,
    state: FSMContext,
):
    await state.update_data({
        city_name: [
            vendor_code,
            search_query,
            page,
            position,
        ]
    })


def _get_position(data: list[dict[str, str]], vendor_code: int,) -> int | None:
    """Returns position of item by vendor_code

    Args:
        data (list[dict[str, str]]): list of items in wb api json (wb_api_json['data']['products'])
        vendor_code (int): compare criteria

    Returns:
        int | None: position if found
    """
    for position, json in enumerate(data, 1):
        if vendor_code == json.get('id'):
            return position
