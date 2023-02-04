import requests
from bs4 import BeautifulSoup
from extract import headers,base_url
from utils import trim


def get_act_details(record):
    _id = record[1].select_one('a')['href'].split('/')[-1]
    return {"id":_id,'name':trim(record[1].get_text()),'date':trim(record[2].get_text()),'approval':trim(record[3].get_text())}


