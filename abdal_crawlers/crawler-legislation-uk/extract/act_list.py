import requests
from bs4 import BeautifulSoup
from extract import headers, base_url
from utils import fix_dir_name


def get_act_list_single_page(url, num):
    f = requests.get(base_url + url + "?page=" + str(num), headers=headers)
    soup = BeautifulSoup(f.content, 'lxml')
    current_page = soup.select("li.currentPage strong")[0].get_text().replace("This is results page ", "")
    if num != int(current_page):
        return []
    acts_query = soup.select("#content tbody tr")
    acts = []
    last = ["", ""]
    for tr in acts_query:
        act = {}
        a = tr.select("td a")
        act['title'] = fix_dir_name(a[0].get_text())
        act['url'] = a[0]['href'][1:]
        if len(a) > 1:
            temp = a[1].get_text().split(" ")
            last = temp
        else:
            temp = last
        act['year'] = temp[0]
        act['number'] = temp[1] if len(temp) > 1 else ''
        acts.append(act)
    return acts


# print(get_act_list_single_page('ukpga',1))
