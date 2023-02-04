import requests
from bs4 import BeautifulSoup

from db.models import Act
from extract import headers, base_url
from utils import convert_xht_to_txt_2


def already_added(url):
    return Act.objects.filter(url=url).exclude(text="").count() > 0


def get_act_details(act):
    # url = base_url + p_id + "?view=extent"
    # f = requests.get(url, headers=headers)
    # soup = BeautifulSoup(f.content, 'lxml')
    # title = soup.select("#pageTitle")[0].get_text()

    temp = act['url'].split("/")
    type_ = temp[0]
    type_ = detect_type(type_, act['title'])
    pdf_url = base_url + act['url'].replace("/contents", "") + "/data.pdf"
    xht_url = base_url + act['url'].replace("/contents", "") + "/data.xht?view=snippet&wrap=true"
    note_pdf_url = base_url + act['url'].replace("/contents", "") + "/note/data.pdf"
    note_xht_url = base_url + act['url'].replace("/contents", "") + "/note/data.xht?view=snippet&wrap=true"
    files = {'.pdf': pdf_url, '.xht': xht_url, '#note.pdf': note_pdf_url, '#note.xht': note_xht_url}
    act['files'] = files
    act['type'] = type_
    if type_ is None:
        # print(f'Act "{act["url"]}" is not  included in accepted types.skipping...')
        act['skipped'] = 'type'
        return act
    if already_added(act['url']):
        # print(f'Act "{act["url"]}" already loaded.skipping...')
        act['skipped'] = 'duplicate'

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
