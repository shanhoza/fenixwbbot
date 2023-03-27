import asyncio
import time
import typing

import aiohttp
import orjson
from aiogram import F, Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from attr import dataclass

from bot import config
from bot.handlers.messages import start as msg
from bot.handlers.user.start import StartCommandStates
from bot.keyboards.inline import START_BACK_KB

router = Router()


@dataclass(frozen=True, slots=True)
class _DataToState:
    vendor_code: int
    search_query: str
    page: int
    position: int
    city: str


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
    result = await _parse_wb_api(message.text.lower())  # type: ignore
    # print(result)
    await message.answer(text='получен vendor_code_and_keyword')
    await state.clear()


def timeit(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            print('this function is a coroutine: {}'.format(func.__name__))
            return await func(*args, **params)
        else:
            print('this is not a coroutine')
            return func(*args, **params)

    async def helper(*args, **params):
        print('{}.time'.format(func.__name__))
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)

        print('>>>', time.time() - start)
        return result

    return helper


@timeit
async def _parse_wb_api(vendor_code_and_search_query: str):
    vendor_code, search_query = vendor_code_and_search_query.split(maxsplit=1)
    async with (
            aiohttp.ClientSession() as session,
            asyncio.TaskGroup() as tg
    ):
        for city_name, city_query in config.WB_API_CITIES_QUERIES.items():
            for page in range(0, config.WB_API_NUMBER_OF_PAGES_TO_PARSE + 1):
                tg.create_task(
                    _get_wb_api_data(
                        session,
                        city_query,
                        page,
                        search_query,
                        int(vendor_code),
                        city_name,
                    )
                )


async def _get_wb_api_data(
        session: aiohttp.ClientSession,
        city_query: str,
        page: int,
        search_query: str,
        vendor_code: int,
        city_name: str,
):

    url = config.WB_API_URL.format(city_query, page, search_query)
    async with session.get(url) as response:
        # todo write to mongo
        try:
            data = orjson.loads(await response.text())
            products = data['data']['products']
        except (KeyError, orjson.JSONDecodeError):
            return
        await asyncio.to_thread(
            _parse_wb_api_json,
            products,
            vendor_code,  # type: ignore
        )


def _parse_wb_api_json(
        data: list[dict[str, str]],
        vendor_code: int,
) -> int | None:

    for position, json in enumerate(data, 1):
        if vendor_code == json.get('id'):
            print(position, vendor_code)
