import sys
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

sys.dont_write_bytecode = True

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

# Import your models for use in your script
from db.models import *
from save.act import export_excel
from request.multi_request import download_all
from extract import base_url
from extract.act import get_act_details
from extract.act_list import get_act_list_single_page
import asyncio


# from utils import load_missing_text


def crawl():
    urls = [
        "ukpga",
        "ukla",
        "uksi",
    ]
    urls_max = [
        90000,
        90000,
        90000,
    ]

    for index, url in enumerate(urls):
        print(f"started fetching '{base_url}{url}' ...")
        page = 0

        count = Act.objects.all().count()
        stored_exception = None
        second_chance = False

        while True:
            page += 1
            page_loaded = Page.objects.filter(url=url, num=page).count() > 0
            if page_loaded:
                continue
            try:
                print(f'fetching page "{base_url}{url}?page={page}"')
                acts = get_act_list_single_page(url, page)
            except KeyboardInterrupt or SystemExit:
                stored_exception = sys.exc_info()
                break
            except Exception as e:
                print(f'error fetching page "{base_url}{url}?page={page} (error:{e})"')
                continue
            if len(acts) == 0 and second_chance:
                break
            second_chance = len(acts) == 0
            dl_urls = {}
            for index_, act in enumerate(acts):
                try:
                    act = get_act_details(act)
                except KeyboardInterrupt or SystemExit:
                    stored_exception = sys.exc_info()
                    break
                except Exception as e:
                    print(f'error fetching act {act["url"]} (error:{e})')
                    continue
                if 'skipped' in act.keys():
                    continue
                if Act.objects.filter(url=act['url']).count() == 0:
                    Act.objects.create(url=act['url'], title=act['title'], type=act['type'], year=act['year'],
                                       number=act['number'], text='')
                dl_urls[act['url']] = act['files']['.xht']
                count += 1

            texts = asyncio.run(download_all(dl_urls))
            for tup in texts:
                if tup is tuple:
                    act = Act.objects.get(url=tup[0])
                    act.text = tup[1]
                    act.save()

            Page.objects.create(url=url, num=page)
            if count >= urls_max[index]:
                stored_exception = "None"
                break

            print(f'total processed acts :{count}')
            if stored_exception:
                print("Either user stopped the process or max act count limit reached!")
                break

        if stored_exception:
            print("Either user stopped the process or max act count limit reached!")
            break

        print(f"finished fetching '{base_url}{url}' ...")


def load_missing_text():
    total = Act.objects.filter(text="empty").count()
    dl_urls = {}
    count = 0
    for act in Act.objects.filter(text="empty"):
        act_temp = get_act_details({'url': act.url, 'title': act.title})
        dl_urls[act.url] = act_temp['files']['.xht']
        if len(dl_urls) == 100:
            texts = asyncio.run(download_all(dl_urls))
            for tup in texts:
                if isinstance(tup, tuple):
                    act_temp2 = Act.objects.get(url=tup[0])
                    act_temp2.text = tup[1]
                    act_temp2.save()
                    count += 1
            dl_urls = {}
            print(f'{count / total}% of {total} done.')


if __name__ == '__main__':
    # crawl()
    export_excel()
    # load_missing_text()
