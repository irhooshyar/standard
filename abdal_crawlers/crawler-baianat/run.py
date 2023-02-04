import sys
import os
import hashlib

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

sys.dont_write_bytecode = True

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

# Import your models for use in your script
from db.models import *
from save.act import export_excel, save_txt
from request.multi_request import download_all
from extract import base_url
from extract.act_list import get_act_list_single_page, get_tickets
import asyncio


# from utils import load_missing_text


def crawl():
    urls = {
        'speech?nt=32&year=':(1350,1405),
        'speech?nt=2&year=':(1350,1405),
    }
    
    docs = list(Doc.objects.all().values_list('id',flat=True))

    for url, pages_range in urls.items():
        print(f"started fetching '{base_url}{url}' ...")
        
        count = len(docs)
        second_chance = False
        page = pages_range[0]

        while page <= pages_range[1]:
            print(f'fetching page "{base_url}{url}?page={page}"')
            if Page.objects.filter(url=url, num=page).exists():
                print('duplicate... skipped.')
                page += 1
                continue
            docs_raw = get_act_list_single_page(url, page)
        
            if len(docs_raw) == 0 and second_chance:
                print('empty page... skipped.')
                second_chance = False
                page += 1
                continue
            second_chance = len(docs_raw) == 0
                
            docs_raw = [doc_raw for doc_raw in docs_raw if doc_raw['id'] not in docs ]
            docs_raw = asyncio.run(download_all(docs_raw))
                        
            bulk = []
            for act in docs_raw:
                bulk.append(Doc(id=act['id'], title=act['title'], date=act['date'], text=act['text'],
                                    labels=act['labels'], type=act['type']))
                
            Doc.objects.bulk_create(bulk)
            docs += [doc.id for doc in bulk]
            count = len(docs)
        
            
            if not second_chance:
                Page.objects.create(url=url, num=page)
                page += 1

            print(f'total processed acts :{count}')

        print(f"finished fetching '{base_url}{url}' ...")
        
        
def crawl_ticket():    
    docs = Doc.objects.all().values_list('id',flat=True)
    urls = {doc:base_url+'newspart-print?id='+str(doc) for doc in docs}
    
    second_chance = False
    index = 0
    ids = list(urls.keys())
    i = 0
    while i < len(ids):
        id = ids[i]
        url = urls[id]
        index += 1
        print(f"started fetching {index}.'{url}' ...")
        
        
        if Doc.objects.get(id=id).tickets_loaded:
            print('already loaded... skipped.')
            i += 1
            continue
        docs_raw = get_tickets(url,id)
    
        if len(docs_raw) == 0 and second_chance:
            print('empty... skipped.')
            second_chance = False
            i += 1
            continue
        second_chance = len(docs_raw) == 0
                                
        bulk = []
        for act in docs_raw:
            bulk.append(Ticket(title=act['title'], doc_id=act['doc_id'], text=act['text'],
                                keywords=act['keywords'], types=act['types']))
            
        Ticket.objects.bulk_create(bulk)    
        
        if not second_chance:
            doc = Doc.objects.get(id=id)
            doc.tickets_loaded = True
            doc.save()
            i += 1

        print(f"finished fetching '{base_url}{url}' ...")


def hashhex(text):
    hash_object = hashlib.sha1(bytes(text,encoding="utf8"))
    return hash_object.hexdigest()

if __name__ == '__main__':
    # crawl()
    # crawl_ticket()
    
    for doc in Doc.objects.all():
        # save_txt("doc/"+doc.title+"_"+str(doc.id),doc.text)

        file_name = doc.title+"_"+str(doc.id)
        hashed_file_name = hashhex(file_name)
        save_txt("doc/"+hashed_file_name,doc.text)
        

    # for ticket in Ticket.objects.all():
    #     save_txt("ticket/"+ticket.title,ticket.text)