import requests
from bs4 import BeautifulSoup
from extract import base_url,page_size
from extract.act import get_act_details


def get_act_list_single_page(page):
    soup = BeautifulSoup(page, 'lxml')
    # print(soup.get_text())
    return [x.select('td') for x in soup.select('table.slwTable tr')[1:]]

# for act in get_act_list_single_page(1):
#     print(get_act_details(act))