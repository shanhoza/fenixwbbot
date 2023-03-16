from typing import Any, Union
import aiohttp
import asyncio
import requests
import time
import json
import traceback
from user_agent2 import generate_user_agent
from asyncio.exceptions import TimeoutError


class Session:
    def __init__(self) -> None:
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def refresh_session(self):
        await self._session.close()
        self._session = None


class Request:
    # Количество повторений запроса, базовое - 5
    RETRY_TIMES = 5
    # Количество неудавшихся запросов, запрос считается неудавшимся, если counter превысил RETRYTIMES
    failed_requests = 0
    # Флаг использования пользовательского класса Session
    custom_session_class = False

    # list_ua = [
    #     'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.88 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    # ]

    def __init__(self):
        pass

    @classmethod
    def get_default(cls, url, counter=0):
        from config import HEADERS
        # from fake_useragent import UserAgent
        import random
        import re

        try:
            # ua = UserAgent()
            headers = {'User-Agent': generate_user_agent(navigator="firefox")}
            # headers = {'User-Agent': random.choice(cls.list_ua)}
            response = requests.get(
                url,
                timeout=1,
                headers=headers
            )
        except Exception as e:
            print(e)
            return None

        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print('Request error', e, url)
                try:
                    return json.loads(response.text)
                except:
                    ar_totals = re.findall('"total":(.*)}}', response.text)
                    if len(ar_totals) > 0:
                        return {'data': {'total': ar_totals[0]}}
                    return None
        elif response.status_code == 429:
            if counter > 15:
                return None

            time.sleep(0.5)
            counter += 1
            return cls.get_default(url, counter=counter)
        elif response.status_code == 504:
            if counter > 15:
                return None

            time.sleep(0.5)
            counter += 1
            return cls.get_default(url, counter=counter)
        else:
            return None

    @classmethod
    async def get(cls, params, keys, url, version=1, return_all=False):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for api_key in keys:
                params['key'] = api_key
                tasks.append(cls.fetch(session, url, params, api_key, version=version, return_all=return_all))
            result = await asyncio.gather(*tasks)
        return result

    @classmethod
    async def fetch(cls, session, url, params, api_key, version=1, return_all=False, counter=0):
        # from fake_useragent import UserAgent
        import random
        from vendor_utils import VendorUtils

        if counter > 5:
            print('Fetch return None', url)
            return None

        # ua = UserAgent()
        headers = {'User-Agent': generate_user_agent(navigator="firefox")}
        # headers = {'User-Agent': random.choice(cls.list_ua)}

        if version > 1:
            headers['Authorization'] = api_key

        result = None
        status = None
        try:
            async with session.get(url, ssl=False, params=params, raise_for_status=not return_all, timeout=10,
                                   headers=headers) as response:
                status = response.status
                if response.status == 200:
                    result = await response.text()
                elif return_all:
                    result = await response.text()
        except TimeoutError:
            counter += 1
            return await cls.fetch(session, url, params, api_key, version=version, return_all=return_all,
                                   counter=counter)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                await asyncio.sleep(1)
            elif e.status == 401:
                if 'key' in params:
                    if version <= 1:
                        if 'key' in params:
                            VendorUtils.un_auth_from_request(params['key'])
                    else:
                        VendorUtils.un_auth_from_request(new_key=params['key'])
                return result
            else:
                pass

            counter += 1
            return await cls.fetch(session, url, params, api_key, version=version, return_all=return_all,
                                   counter=counter)
        except aiohttp.ClientConnectionError:
            print("Oops, the connection was dropped before we finished")
            counter += 1
            return await cls.fetch(session, url, params, api_key, version=version, return_all=return_all,
                                   counter=counter)
        except Exception as e:
            print('Error fetch', e)
            # traceback.print_exc()
            return {
                'key': api_key,
                'data': result
            }

        if status == 429:
            print("Too many requests waiting...")
            await asyncio.sleep(0.5)
            counter += 1
            return await cls.fetch(session, url, params, api_key, version=version, return_all=return_all,
                                   counter=counter)
        elif status == 504:
            await asyncio.sleep(0.5)
            counter += 1
            return await cls.fetch(session, url, params, api_key, version=version, return_all=return_all,
                                   counter=counter)
        elif status == 500:
            print("Error in server retake...")
            counter += 1
            return await cls.fetch(session, url, params, api_key, version=version, return_all=return_all,
                                   counter=counter)

        return {
            'key': api_key,
            'data': result
        }

    @classmethod
    async def fetch_search_products(cls, session, url, key):
        result = []
        try:
            async with session.get(url, ssl=False, raise_for_status=True, timeout=60) as response:
                if response.status == 200:
                    response = await response.text()
            try:
                data = json.loads(response)
                if 'catalog' in data and 'data' in data['catalog'] and 'products' in data['catalog']['data']:
                    for index, product in enumerate(data['catalog']['data']['products']):
                        result.append({
                            'text_search': data['name'],
                            'nmId': product['id'],
                            'key': key,
                            'place': index
                        })
                elif 'data' in data and 'products' in data['data']:
                    if len(data['data']['products']) > 0:
                        for index, product in enumerate(data['data']['products']):
                            result.append({
                                'text_search': data['metadata']['name'],
                                'nmId': product['id'],
                                'key': key,
                                'place': index
                            })

            except Exception as e:
                print('Error parse json', e, url)
        except Exception as e:
            print(e)
            return result
        finally:
            return result

    @classmethod
    async def fetch_raw(cls, session: Union[aiohttp.ClientSession, Session], url: str, is_json=True, counter=0):
        # from fake_useragent import UserAgent
        import random

        if counter > cls.RETRY_TIMES:
            # Отслеживание количества неудавшихся запросов
            # При превышении установленного числа обновляем сессию
            cls.failed_requests += 1
            if cls.failed_requests >= 2 and cls.custom_session_class:
                cls.failed_requests = 0
                print('Refreshing session...')
                await session.refresh_session()

            print('Fetch Raw return None', url)
            return None

        if isinstance(session, Session):
            session = session.session

        # ua = UserAgent()
        headers = {'User-Agent': generate_user_agent(navigator="firefox")}
        # headers = {'User-Agent': random.choice(cls.list_ua)}
        result = None
        status = None
        try:
            async with session.get(url, raise_for_status=True, timeout=5, headers=headers) as response:
                status = response.status
                if response.status == 200:
                    if is_json:
                        response = await cls.try_to_get_json(response)
                    else:
                        response = await response.text()
                else:
                    print('Response', response, response.status)
                    response = None
            result = response
        except TimeoutError:
            counter += 1
            return await cls.fetch_raw(session, url, is_json=is_json, counter=counter)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                await asyncio.sleep(0.5)
            else:
                print("ClientResponseError", e)

            counter += 1
            return await cls.fetch_raw(session, url, is_json=is_json, counter=counter)
        except aiohttp.ClientConnectionError as e:
            if counter == cls.RETRY_TIMES:
                print("Oops, the connection was dropped before we finished", e)
            counter += 1
            return await cls.fetch_raw(session, url, is_json=is_json, counter=counter)
        except Exception as e:
            print('Error Fetch Raw', e)
            traceback.print_exc()
            return result

        if status == 429:
            print("Too many requests waiting...")
            await asyncio.sleep(0.5)
            counter += 1
            return await cls.fetch_raw(session, url, is_json=is_json, counter=counter)
        elif status == 504:
            await asyncio.sleep(0.5)
            counter += 1
            return await cls.fetch_raw(session, url, is_json=is_json, counter=counter)
        elif status == 500:
            print("Error in server retake...")
            counter += 1
            return await cls.fetch_raw(session, url, is_json=is_json, counter=counter)

        return result

    @classmethod
    async def fetch_api_raw(cls, session, url, key, params, is_json=True, version=1, api_key=None, counter=0):
        # from fake_useragent import UserAgent
        import random
        from vendor_utils import VendorUtils

        result = (key, None)

        if counter > 5:
            print('Fetch API Raw return None', url, params)
            return result

        # ua = UserAgent()
        headers = {'User-Agent': generate_user_agent(navigator="firefox")}
        # headers = {'User-Agent': random.choice(cls.list_ua)}

        if version > 1:
            headers['Authorization'] = api_key

        status = None
        try:
            async with session.get(url, params=params, raise_for_status=True, timeout=20, headers=headers) as response:
                status = response.status
                if response.status == 200:
                    if is_json:
                        response = await cls.try_to_get_json(response)
                    else:
                        response = await response.text()
                else:
                    print('Response', response, response.status)
                    response = None
            result = (key, response)
        except TimeoutError:
            counter += 1
            return await cls.fetch_api_raw(
                session, url, key, params, is_json=is_json, version=version, api_key=api_key, counter=counter
            )
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                await asyncio.sleep(1)
            if e.status == 401:
                if version <= 1:
                    if 'key' in params:
                        VendorUtils.un_auth_from_request(params['key'])
                    else:
                        VendorUtils.un_auth_from_request(supplier_id=key)
                else:
                    VendorUtils.un_auth_from_request(new_key=api_key)
                return result
            else:
                print("ClientResponseErrorApiRaw", e)

            counter += 1
            return await cls.fetch_api_raw(
                session, url, key, params, is_json=is_json, version=version, api_key=api_key, counter=counter
            )
        except aiohttp.ClientConnectionError as e:
            print("Oops, the connection was dropped before we finished", e)
            counter += 1
            return await cls.fetch_api_raw(
                session, url, key, params, is_json=is_json, version=version, api_key=api_key, counter=counter
            )
        except Exception as e:
            print('Error Fetch API Raw', e)
            traceback.print_exc()
            return result

        if status == 429:
            print("Fetch API Raw Too many requests waiting...")
            await asyncio.sleep(1)
            print('Await sleep complete')
            counter += 1
            return await cls.fetch_api_raw(
                session, url, key, params, is_json=is_json, version=version, api_key=api_key, counter=counter
            )
        if status == 504:
            await asyncio.sleep(0.5)
            counter += 1
            return await cls.fetch_api_raw(
                session, url, key, params, is_json=is_json, version=version, api_key=api_key, counter=counter
            )
        elif status == 500:
            print("Error in server retake...")
            counter += 1
            return await cls.fetch_api_raw(
                session, url, key, params, is_json=is_json, version=version, api_key=api_key, counter=counter
            )

        return result

    @classmethod
    async def fetch_fbs_api_raw(cls, session, url, key, params, api_key, is_json=True, is_new=False, counter=0):
        # from fake_useragent import UserAgent
        import random
        from vendor_utils import VendorUtils

        result = (key, None)
        if counter > 5:
            print('FBS Fetch API Raw return None', url, params, api_key)
            return result

        # ua = UserAgent()
        headers = {'User-Agent': generate_user_agent(navigator="firefox"), 'Authorization': api_key}
        # headers = {'User-Agent': random.choice(cls.list_ua), 'Authorization': api_key}
        try:
            async with session.get(url, params=params, raise_for_status=True, timeout=20, headers=headers) as response:
                status = response.status
                if response.status == 200:
                    if is_json:
                        response = await cls.try_to_get_json(response)
                    else:
                        response = await response.text()
                else:
                    print('Response', response, response.status)
                    response = None
            result = (key, response)
        except TimeoutError:
            counter += 1
            return await cls.fetch_fbs_api_raw(
                session, url, key, params, api_key, is_json=is_json, is_new=is_new, counter=counter
            )
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                await asyncio.sleep(1)
            elif e.status == 401:
                VendorUtils.un_auth_fbs_request(api_key, is_new=is_new)
                return result
            else:
                print("ClientResponseErrorApiRaw", e)

            counter += 1
            return await cls.fetch_fbs_api_raw(
                session, url, key, params, api_key, is_json=is_json, is_new=is_new, counter=counter
            )
        except aiohttp.ClientConnectionError as e:
            print("Oops, the connection was dropped before we finished", e)
            counter += 1
            return await cls.fetch_fbs_api_raw(
                session, url, key, params, api_key, is_json=is_json, is_new=is_new, counter=counter
            )
        except Exception as e:
            print('Error Fetch FBS API Raw', e)
            traceback.print_exc()
            return result

        if status == 429:
            print("Fetch FBS API Raw Too many requests waiting...")
            await asyncio.sleep(1)
            print('Await sleep complete')
            counter += 1
            return await cls.fetch_fbs_api_raw(
                session, url, key, params, api_key, is_json=is_json, is_new=is_new, counter=counter
            )
        elif status == 504:
            await asyncio.sleep(0.5)
            counter += 1
            return await cls.fetch_fbs_api_raw(
                session, url, key, params, api_key, is_json=is_json, is_new=is_new, counter=counter
            )
        elif status == 500:
            print("Error in server retake...")
            counter += 1
            return await cls.fetch_fbs_api_raw(
                session, url, key, params, api_key, is_json=is_json, is_new=is_new, counter=counter
            )

        return result

    @staticmethod
    async def try_to_get_json(content):
        result = None
        try:
            result = await content.json()
        except:

            try:
                response = await content.text()
                result = json.loads(response)
            except:
                pass

        return result
