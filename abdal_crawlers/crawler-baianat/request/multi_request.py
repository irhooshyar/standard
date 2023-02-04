import asyncio
import aiohttp
from aiohttp.client import ClientSession
from asgiref.sync import sync_to_async

from db.models import Doc
from extract import headers, base_url, types_
from utils import convert_xht_to_txt_2
from bs4 import BeautifulSoup
import nest_asyncio
nest_asyncio.apply()


async def download_link(doc: dict, session: ClientSession):
    url = base_url + types_[doc['type']] + str(doc['id'])
    response = await session.get(url=url, headers=headers)
    doc['text'] = ''
    doc['labels'] = ''
    result = await response.text()
    # result = result.replace('<br>','\n')
    soup = BeautifulSoup(result, 'lxml')
    try:
        doc['text'] = soup.select("div.Content")[0].get_text()
    except Exception as e:
        print(e.__str__)

    acts_query = soup.select("div#newsContentInnerSide > div")
    for tr in acts_query:
        if not tr.has_attr('style') or tr['style'] != 'width: 100%;overflow:hidden;display:inline; background: #ffffff; float:right':
            continue
        div_tags = tr.select("div")
        for tr_ in div_tags:
            if not tr_.has_attr('style') or tr_['style'] != 'display:inline;float:right;margin:12px ;line-height:23px;color:#444':
                continue
            a_tags = tr_.select("a")
            for a_tag in a_tags:
                doc['labels'] += a_tag.get_text()
    return doc


async def download_all(urls: list):
    my_conn = aiohttp.TCPConnector(limit=4)
    session = aiohttp.ClientSession(connector=my_conn)
    results = await asyncio.gather(*[download_link(doc, session) for doc in urls])
    await session.close()
    return results
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for doc in urls:
            task = asyncio.ensure_future(download_link(doc, session=session))
            tasks.append(task)
        texts = await asyncio.gather(*tasks, return_exceptions=True)  # await must be nested inside the session
    return texts
