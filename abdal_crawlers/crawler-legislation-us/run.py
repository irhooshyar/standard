import asyncio
import sys
import os
import time

from save import files_dir

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

sys.dont_write_bytecode = True

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

from db.models import *
from extract import base_url
from extract.legislation import get_act_details
from save.legislation import dl_file
from extract.legislation_list import get_act_list_single_page
from django.db.models import Count

from request.multi_request import download_all


def crawl():
    urls = [
        'search?q=%7B"source"%3A"legislation"%2C"congress"%3A"all"%2C"bill-status"%3A"law"%7D&pageSort=latestAction%3Aasc&pageSize=250',
        'search?q={"source":"legislation","congress":"all","bill-status":"law"}&pageSort=latestAction%3Adesc&pageSize=250',
    ]

    for index, url in enumerate(urls):
        print(f"started fetching '{base_url}{url}' ...")
        page_objs = Page.objects.filter(url=url)
        page = 0

        total_count = Legislation.objects.all().count()
        second_chance = False

        while True:
            page += 1
            if page_objs.filter(num=page).count() > 0:
                continue
            # try:
            print(f"fetching page '{base_url}{url}&page={page}'")
            acts = get_act_list_single_page(url, page)
            # except Exception as e:
            #     Page.objects.create(url=url, num=page, count=0, status=e.__str__())
            #     print(f'error fetching page "{base_url}{url}?page={page} ({e.__str__()})"')
            #     continue
            if len(acts) == 0:
                if second_chance:
                    break
                else:
                    second_chance = True
                    page -= 1
                    continue

            for index_, act in enumerate(acts):
                try:
                    act = get_act_details(act)
                except Exception as e:
                    print(f'error fetching act {act["url"]} (error:{e.__str__()})')
                    continue

            create_list = []
            count = 0
            for act in acts:
                create_list.append(Legislation(**act))
                count += 1
                pass
            break_ = False
            try:
                Legislation.objects.bulk_create(create_list)
                result = 'done'
            except Exception as e1:
                for item in create_list:
                    try:
                        item.save()
                    except Exception as e2:
                        print(e2.__str__())
                        print(f'error in saving {item}')
                result = e1.__str__()
                break_ = True
            Page.objects.create(url=url, num=page, count=count, status=result)
            total_count += count
            if break_:
                break

            print(f'total processed acts :{total_count}')

        print(f"finished fetching '{base_url}{url}' ...")


def handle_duplicate_title():
    dup_titles = Legislation.objects.values('title').annotate(repeat_count=Count('title')).order_by() \
        .filter(repeat_count__lt=1)

    for dup_title in dup_titles:
        duplicates = Legislation.objects.filter(title=dup_title['title'])
        for duplicate in duplicates:
            duplicate.title = duplicate.title + " " + duplicate.code_name + " — " + duplicate.congress
            duplicate.save()

    return


def fetch_text():
    legis = Legislation.objects.exclude(text_url__isnull=True)
    legis = legis.filter(text='') | legis.filter(text__isnull=True) | legis.filter(text='empty') | legis.filter(text='blocked')
    print(f'{len(legis)} remaining...')
    legis = legis.values('text_url', 'id')
    # legis = legis[:100]
    dl_urls = {}
    for legi in legis:
        dl_urls[legi['id']] = legi['text_url']
    texts = asyncio.run(download_all(dl_urls, 1))
    for tup in texts:
        try:
            legi = Legislation.objects.get(id=tup['index'])
            legi.text = tup['text']
            legi.save()
        except Exception as e:
            print(e.__str__())


if __name__ == '__main__':
    crawl()

    # handle_duplicate_title()

    # count = 0
    # while count < 1000:
    #     fetch_text()
    #     count += 1
    #     time.sleep(5)
    #     print(count)
    #     print("________________________________")

    # Legislation.objects.exclude(text_url__isnull=True).update(text=None)

    # legis = Legislation.objects.exclude(text__isnull=True).exclude(text='').exclude(text='empty').exclude(
    #     text='blocked')
    # for legi in legis:
    #     save_txt(legi.title, legi.text)
    # export_excel()
    # load_missing_text()

    loaded_pdf = os.listdir(files_dir + "/pdf/")

    legis = Legislation.objects.filter(pdf_url__isnull=False)
    legis = legis.filter(text__isnull=True) | legis.filter(text='') | legis.filter(text='empty') | legis.filter(text='blocked')
    total = legis.count()
    count = 0
    for legi in legis:
        count += 1
        file_name = legi.title+".pdf"
        if file_name in loaded_pdf:
            continue
        print(f'{count} of {total}')
        dl_file(base_url + legi.pdf_url, file_name,'pdf')
        # break

