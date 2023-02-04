import re

import requests
from bs4 import BeautifulSoup

from db.models import Legislation
from extract import headers, base_url
from utils import fix_dir_name
import json


def get_act_list_single_page(url, config):

    response = requests.request("POST", base_url+url, headers=headers, data=config, files=[])
    acts_dict = json.loads(response.text)
    acts = []
    for act in acts_dict['results']:
        acts.append(Legislation(
            id=act['Id'],
            statement_digest=act['StatementDigest'],
            judgment_number = act['JudgmentNumber'],
            judgment_approve_date_persian = act['JudgmentApproveDatePersian'],
            complaint_serial = act['ComplaintSerial'],
            conclusion_display_name = act['ConclutionDisplayName'],
        ))
    return acts




# print(get_act_list_single_page('ukpga',1))
