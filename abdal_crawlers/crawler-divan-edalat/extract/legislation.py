import json

import requests
from bs4 import BeautifulSoup

# from db.models import Act
from db.models import Legislation
from extract import headers, base_url
from utils import convert_xht_to_txt_2




def get_act_details(act, url,config):
    response = requests.request("GET", base_url+url+config['params']+str(act.id), headers=headers, data={})
    act_dict = json.loads(response.text)
    act.laws = act_dict['details']['laws']
    html = act_dict['details']['content']
    soup = BeautifulSoup(html, 'lxml')
    text_div = soup.find("body")
    text_tags = text_div.findChildren(recursive=False)
    text = [text_tag.getText().strip() for text_tag in text_tags]
    act.content = "\n".join(text)
    act.subject_type_display_name = act_dict['details']['subjectTypeDisplayName']
    act.judgment_type = act_dict['details']['judgmentType']
    act.complainant = act_dict['details']['complainant']
    act.complaint_from = act_dict['details']['complaintFroms']
    act.categories = act_dict['details']['category']
    return act



def get_txt(url):
    f = requests.get(url, headers=headers)
    soup = BeautifulSoup(f.content, 'lxml')
    for script in soup(["script", "style", "head"]):
        script.extract()
    return soup


def clean_txt(text):
    soup = BeautifulSoup(text, 'lxml')
    for script in soup(["script", "style", "head"]):
        script.extract()
    return soup


# def get_links(url):
#     f = requests.get(url, headers=headers)
#     soup = BeautifulSoup(f.content, 'lxml')
#     links = []
#     tags = soup.find_all("a")
#     for tag in tags:
#         if "href" in str(tag) and str(tag['href']).startswith(base_url):
#             links.append(tag['href'])
#     return links


def get_act_txt(url):
    text = get_txt(url)
    text = convert_xht_to_txt_2(str(text))
    if len(text) == 0:
        raise Exception(f"failed to load ({url})'s text")
    return text


accepted_types = {
    'uksi': 'UK Statutory Instruments',
    # 'ukci': 'Church Instruments',
    # 'uksro': 'Statutory Rules and Orders',
    'ukpga': 'Public General Acts',
    'ukla': 'Local Acts',
    # 'ukcm': 'Church of England Measures',
}

uksi = [
    "Order",
    "Regulations",
    "Rules",
    "Scheme",
    "Direction",
    "Declaration",
]


def detect_type(_type, title):
    if _type == "uksi":
        return detect_uksi_type(title)
    elif _type in accepted_types.keys():
        return accepted_types[_type]
    else:
        return None


def detect_uksi_type(title: str):
    title = title.lower()
    title = title.replace("order of council", "", len(title))
    indices = []
    for uksi_ in uksi:
        indices.append(title.rfind(uksi_.lower()))
    max_ = indices.index(max(indices))
    if max(indices) == -1:
        return "unknown"
    return uksi[max_]
