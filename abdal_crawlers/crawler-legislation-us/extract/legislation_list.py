import re

import requests
from bs4 import BeautifulSoup
from extract import headers, base_url
from utils import fix_dir_name


def get_act_list_single_page(url, num):
    f = requests.get(base_url + url + "&page=" + str(num), headers=headers)
    soup = BeautifulSoup(f.content, 'lxml')
    complete_text = soup.get_text()
    if "Too Many Requests." in complete_text or 'The page you requested is unavailable.' in complete_text:
        return []
    legis_query = soup.select("div#main ol li.expanded")
    legises = []
    for legis in legis_query:
        act = {'type':'law'}
        try:
            temp = legis.select("span.result-heading")[0]
            temp1 = temp.select("a")[0]
            act['url'] = temp1.get('href').split('?')[0].strip()
            temp2 = legis.select("span.result-title")[0]
            act['title'] = fix_dir_name(temp2.get_text()).strip()
            act['code_name'] = temp1.get_text().strip()
        except Exception as e:
            print('1.'+e.__str__())
            continue

        act['congress'] = temp.get_text()
        act['congress'] = act['congress'].replace(act['code_name'],'').replace('—','').strip()
        temps = legis.select("span.result-item:not(.result-tracker)")
        for temp in temps:
            try:
                strong_tag = temp.select('strong')[0].get_text()
            except Exception as e:
                print('2.'+e.__str__())
                continue
            if strong_tag == 'Sponsor:':
                act['introduce_date'] = temp.get_text()
                try:
                    temp = temp.select("a")[0]
                    act['sponsor'] = temp.get_text().strip()
                    act['introduce_date'] = act['introduce_date'].replace(act['sponsor'], '').replace(strong_tag,'') \
                        .replace('(Introduced', '').replace(')', '').split('Cosponsors')[0].strip()
                except Exception as e:
                    print('3.'+e.__str__())
            elif strong_tag == 'Committees:':
                act['committees'] = temp.get_text().replace(strong_tag, '').strip()
            elif strong_tag == 'Latest Action:':
                temp_text = temp.get_text()
                temp_text = temp_text.replace('.','').replace('|','').replace(':','').replace('(','').replace(')','')
                temp_text = re.sub('[a-zA-Z]', '', temp_text).split(" ")
                temp_text = [te for te in temp_text if te.strip() != '']
                try:
                    act['became_law_date'] = temp_text[0].strip()
                    act['number'] = temp_text[-1].strip()
                except Exception as e:
                    print('6.' + e.__str__())
                a_tags = temp.select('a')
                for a_tag in a_tags:
                    a_tag_text = a_tag.get_text()
                    if 'TXT' in a_tag_text:
                        try:
                            act['text_url'] = a_tag.get('href').strip()
                        except Exception as e:
                            print('4.'+e.__str__())
                    elif 'PDF' in a_tag_text:
                        try:
                            act['pdf_url'] = a_tag.get('href').strip()
                        except Exception as e:
                            print('5.'+e.__str__())
        legises.append(act)
    return legises


# print(get_act_list_single_page('ukpga',1))
