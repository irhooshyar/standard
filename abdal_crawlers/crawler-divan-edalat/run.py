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
from save.legislation import dl_file, save_txt
from extract.legislation_list import get_act_list_single_page
from django.db.models import Count

from request.multi_request import download_all


def crawl(list_url, list_config, item_url, item_config):
    ids = Legislation.objects.all().values_list('id',flat=True)
    print(f"started fetching '{base_url}{list_url}' ...")
    # pages = Page.objects.filter(url=list_url).values_list('config', flat=True)
    page = 0

    total_count = Legislation.objects.all().count()
    second_chance = False

    while True:
        page += 1
        # if page_loaded({**list_config,'Page': page}, pages):
        #     print(f"page {page} already loaded.")
        #     continue
        try:
            print(f"fetching page '{base_url}{list_url}&page={page}'")
            acts = get_act_list_single_page(list_url, {**list_config, 'Page': page})
        except Exception as e:
            # Page.objects.create(url=url, num=page, count=0, status=e.__str__())
            print(f'error fetching page "{base_url}{list_url}?page={page} ({e.__str__()})"')
            continue
        if len(acts) == 0:
            if second_chance:
                break
            else:
                second_chance = True
                page -= 1
                continue

        for index_, act in enumerate(acts):
            try:
                if int(act.id) in ids:
                    continue
                act = get_act_details(act, item_url, item_config)
            except Exception as e:
                print(f'error fetching act {act.id} (error:{e.__str__()})')
                continue

        count = 0
        try:
            Legislation.objects.bulk_create(acts)
            count += len(acts)
        except Exception as e1:
            for item in acts:
                try:
                    item.save()
                    count += 1
                except Exception as e2:
                    print(e2.__str__())
                    print(f'error in saving {item}')
        total_count += count

        print(f'total processed acts :{total_count}')

    print(f"finished fetching '{base_url}{list_url}' ...")


def page_loaded(config, pages):
    for page in pages:
        if config == page:
            return True
    return False


def fetch_text(item_url, item_config):
    legis = Legislation.objects.filter(content__isnull=True)
    total = legis.count()
    count = 0
    for legi in legis:
        count += 1
        print(f'{round(count/total,2)*100}%')
        try:
            legi = get_act_details(legi, item_url, item_config)
            legi.save()
        except Exception as e:
            print(f'error fetching act {legi.id} (error:{e.__str__()})')
            continue


if __name__ == '__main__':
    _list_url = 'Assistances/FindQuickSearchResults'
    _list_config = {
        'term': '',
        'quickSearchPath': 'AssistanceContent',
        'container': 'assistance',
        'SearchInCategory': 'true',
        'SearchInContent': 'false',
        'SearchInJudgmentNumber': 'true',
        'SearchInSerial': 'true',
        'SearchInStatementDigest': 'true',
        'CategoryIds': '',
        'SortBy': 'JudgmentIssueDateDescending',
        'JudgmentTypeCompressed': '1,2',
        'GCAssistanceConclutionTypeCompressed': '1'
    }
    _item_url = 'Assistances/GetGCSearchDetailModal'
    _item_config = {'params':'?_=1661414430900&Id='}
    # crawl(_list_url, _list_config, _item_url, _item_config)
    while Legislation.objects.filter(content__isnull=True).count() > 0:
        fetch_text(_item_url, _item_config)

    # handle_duplicate_title()

    # count = 0
    # while count < 1000:
    #     fetch_text()
    #     count += 1
    #     time.sleep(5)
    #     print(count)
    #     print("________________________________")

    # Legislation.objects.exclude(text_url__isnull=True).update(text=None)

    # legis = Legislation.objects.all()
    # for legi in legis:
    #     save_txt(str(legi.id), legi.text)
    # export_excel()
    # load_missing_text()

    # loaded_pdf = os.listdir(files_dir + "/pdf/")
    #
    # legis = Legislation.objects.filter(pdf_url__isnull=False)
    # legis = legis.filter(text__isnull=True) | legis.filter(text='') | legis.filter(text='empty') | legis.filter(text='blocked')
    # total = legis.count()
    # count = 0
    # for legi in legis:
    #     count += 1
    #     file_name = legi.title+".pdf"
    #     if file_name in loaded_pdf:
    #         continue
    #     print(f'{count} of {total}')
    #     dl_file(base_url + legi.pdf_url, file_name,'pdf')
    # break
