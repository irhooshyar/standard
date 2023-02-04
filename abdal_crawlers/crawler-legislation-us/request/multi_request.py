import asyncio
import aiohttp
from aiohttp.client import ClientSession
from asgiref.sync import sync_to_async

from bs4 import BeautifulSoup

from extract import base_url
from extract.legislation import clean_txt
# from request import my_conn
from utils import convert_xht_to_txt_2
import nest_asyncio

nest_asyncio.apply()


async def download_link(url: str, pid: str, session: ClientSession):
    # print(f'download_link ran with {pid} outside')
    async with session.get(url) as response:
        # print(f'download_link ran with {pid} inside')
        result = await response.text()
        # print(f'download_link ran with {pid} result is {result}')
        text = clean_txt(result)
        text = convert_xht_to_txt_2(str(text)).strip()
        if '# 403 ERROR' in text:
            print("blocked")
            text = 'blocked'
            # exit(88)
        if '' == text:
            text = 'empty'
        return {'index': pid, 'text': text}


async def custom_download_link_1(url: str, pid: str, session: ClientSession):
    async with session.get(url) as response:
        try:
            # print(url)
            result = await response.text()
            result = BeautifulSoup(result, 'lxml')
            # print(result.select('#billTextContainer'))
            text = result.select('#billTextContainer')[0].get_text()
            # text = clean_txt(text)
            # text = convert_xht_to_txt_2(str(text)).strip()
        except Exception as e:
            print(f'{e.__str__()} - {url}')
            text = ''
        if '# 403 ERROR' in text:
            print("blocked")
            text = 'blocked'
            # exit(88)
        if '' == text:
            text = 'empty'
        return {'index': pid, 'text': text}


async def download_all(urls: dict, custom: int):
    my_conn = aiohttp.TCPConnector(limit=1)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for key in urls.keys():
            url = urls[key]
            if custom == 1:
                task = asyncio.ensure_future(custom_download_link_1(url=base_url[:-1] + url, pid=key, session=session))
            else:
                task = asyncio.ensure_future(download_link(url=url, pid=key, session=session))
            tasks.append(task)
        texts = await asyncio.gather(*tasks, return_exceptions=True)  # await must be nested inside the session
    return texts
