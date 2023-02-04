import asyncio
import aiohttp
from aiohttp.client import ClientSession
from asgiref.sync import sync_to_async

# from request import my_conn
import nest_asyncio
nest_asyncio.apply()


async def download_link(url: str, pid: str, session: ClientSession):
    # print(f'download_link ran with {pid} outside')
    async with session.get(url) as response:
        # print(f'download_link ran with {pid} inside')
        text = await response.text()
        # print(f'download_link ran with {pid} result is {result}')
        # text = clean_txt(result)
        # text = convert_xht_to_txt(str(text)).strip()
        # if '# 403 ERROR' in text:
        #     print("blocked")
        #     text = 'blocked'
        #     exit(88)
        # if '' == text:
        #     text = 'empty'
        return pid, text


async def download_all(urls: dict):
    my_conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for key in urls.keys():
            url = urls[key]
            task = asyncio.ensure_future(download_link(url=url, pid=key, session=session))
            tasks.append(task)
        texts = await asyncio.gather(*tasks, return_exceptions=True)  # await must be nested inside the session
    return texts
