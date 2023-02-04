from tkinter.messagebox import NO
import requests
from bs4 import BeautifulSoup
from extract import headers, base_url, types
from utils import fix_dir_name


def get_act_list_single_page(url, num):
    f = requests.get(base_url + url + str(num), headers=headers)
    soup = BeautifulSoup(f.content, 'lxml')
    acts_query = soup.select("div.AccBoxHead h2 a")
    acts = []
    for tr in acts_query:
        act = {'id':int(tr['href'].split('id=')[-1]),'title':fix_dir_name(tr['title'])}
        try:
            act['date'] = tr.select("span")[0].get_text()
        except Exception as e:
            act['date'] = None
            print(e.__str__)
        act['type'] = types[url]['name']
        acts.append(act)
    return acts


def get_tickets(url,doc):
    f = requests.get(url, headers=headers)
    soup = BeautifulSoup(f.content, 'lxml')
    try:
        soup = soup.select('table')[1]
        acts_query = soup.find("td").prettify().split('<hr>')
    except Exception as e:
        print(e.__str__)
        return []
    acts = []
    for tr in acts_query:
        act = {}
        text = BeautifulSoup(tr, 'lxml').get_text()
        
        act['title'] = text.split('کلیدواژه(ها) :')[0].split('عنوان فیش :')[-1].strip()
        
        if "[ بازگشت ]" in act['title']:
            continue
        
        act['title'] = fix_dir_name(act['title'])
        
        act['text'] = text.split('متن فیش :')[-1].strip()
            
        act['doc_id'] = doc

        act['keywords'] = text.split('نوع(ها) :')[0].split('کلیدواژه(ها) :')[-1].strip().replace("\n","")

        act['types'] = text.split('متن فیش :')[0].split('نوع(ها) :')[-1].strip().replace("\n","")
        
        acts.append(act)
    return acts
