import asyncio

from bs4 import BeautifulSoup
import pandas as pd
import sys

from request.multi_request import download_all

sys.dont_write_bytecode = True
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

from db.models import Law
from os import listdir
from os.path import isfile, join

base_dir = r"extracted_data"
files_list_dir = base_dir + r"/data.xlsx"


def make_excel():
    Excel_file = pd.DataFrame({'id': [], 'title': [],
                               'TasvibDate': [], 'EblaghieDate': [], 'row_MarjaeTasvib': [],
                               'Mainlink': [], 'PrintLink': [], 'noe_ghanon': [],
                               'tabaghe_bandi': [], 'shomare_sanad_tasvib': [], 'shomare_eblagh': [],
                               'marjae_eblagh': [], 'tarikh_ejra': [], 'akharin_vaziat': [],
                               'dastgah_mojri': [], 'ronevesht': [], 'has_text': []})
    index = 0
    for law in Law.objects.all():
        Excel_file.at[index, "id"] = law.pid
        Excel_file.at[index, "title"] = law.name
        Excel_file.at[index, "TasvibDate"] = law.data
        Excel_file.at[index, "row_MarjaeTasvib"] = law.approve
        Excel_file.at[index, "noe_ghanon"] = law.noe_ghanon
        Excel_file.at[index, "tabaghe_bandi"] = law.tabaghe_bandi
        Excel_file.at[index, "shomare_sanad_tasvib"] = law.shomare_sanad_tasvib
        Excel_file.at[index, "shomare_eblagh"] = law.shomare_eblagh
        Excel_file.at[index, "EblaghieDate"] = law.tarikh_eblagh
        Excel_file.at[index, "marjae_eblagh"] = law.marjae_eblagh
        Excel_file.at[index, "tarikh_ejra"] = law.tarikh_ejra
        Excel_file.at[index, "akharin_vaziat"] = law.akharin_vaziat
        Excel_file.at[index, "dastgah_mojri"] = law.dastgah_mojri
        Excel_file.at[index, "ronevesht"] = law.ronevesht
        Excel_file.at[index, "has_text"] = law.has_text
        index += 1
        if index % 1000 == 0:
            print(f'loaded {index} laws.')

    Excel_file.to_excel(base_dir + r"/result_List_with_features.xlsx", index=False)


def fix_dir_name(name: str):
    return name.replace("\\", "-").replace("/", "-").replace(":", "-").replace("*", "-").replace('"', "-"). \
        replace("<", "-").replace(">", "-").replace("|", "-").replace("?", "-").replace("\u200c", " ").\
        replace("\n", " ")


def crawl():
    Excel_file = pd.read_excel(files_list_dir)
    print("Read Excel File: Done")
    total = len(Excel_file)

    dl_urls = {}
    for index, row in Excel_file[::-1].iterrows():
        id__ = str(row["pid"])
        if Law.objects.filter(pid=id__, status='done').count() > 0:
            continue
        Attribute_URL = "https://qavanin.ir/Law/Attribute/" + id__
        Text_URL = "https://qavanin.ir/Law/TreeText/" + id__
        dl_urls[id__ + "#Attribute_URL"] = Attribute_URL
        dl_urls[id__ + "#Text_URL"] = Text_URL
        if Law.objects.filter(pid=id__).count() == 0:
            Law.objects.create(pid=id__, name=fix_dir_name(str(row["name"]).strip()), approve=str(row["approval"]),
                               data=str(row["date"]), status='empty')
        if len(dl_urls.keys()) >= 100:
            multi_request(dl_urls)
            print(f'loaded {total - index + 1} laws.')
            dl_urls = {}

    make_excel()


def multi_request(dl_urls):
    texts = asyncio.run(download_all(dl_urls))
    for tup in texts:
        try:
            if isinstance(tup, tuple):
                temp = tup[0].split("#")
                id_ = temp[0]
                if temp[1] == 'Attribute_URL':
                    temp = Law.objects.filter(pid=id_).exclude(status='done').exclude(status='detail')
                    if temp.count() == 0:
                        continue
                    else:
                        temp = temp[0]
                    law = {}
                    Attribute_Page = tup[1]
                    Attribute_soup = BeautifulSoup(Attribute_Page, features="html.parser")
                    table_tag = Attribute_soup.find_all("table")[2]
                    tr_tag = table_tag.find_all("tr")

                    doc_attribute_dictionary = {}

                    for i in range(tr_tag.__len__()):
                        td_tag = tr_tag[i].find_all("td")
                        for td in td_tag:
                            td_tag_0 = td
                            span_tag = td_tag_0.find_all("span")[0]
                            span_0_key = span_tag.text.rstrip().lstrip().replace(":", "")
                            span_0_value = str(td_tag_0).replace(str(span_tag), "").replace("<td>", "").replace(
                                "</td>",
                                "").rstrip().lstrip()
                            doc_attribute_dictionary[span_0_key] = span_0_value

                    div_tag = Attribute_soup.find_all("div", {"class": "tab-content tabs"})[0].find_all("div")

                    # Mojri
                    mojri_span_tag = div_tag[1].find_all("span")[0].contents
                    mojri_list = [r.rstrip().lstrip() for r in mojri_span_tag if str(r) != "<br/>"]

                    # Ronevesht
                    ronevesht_span_tag = div_tag[2].find_all("span")[0].contents
                    ronevesht_list = [r.rstrip().lstrip() for r in ronevesht_span_tag if str(r) != "<br/>"]

                    law["noe_ghanon"] = doc_attribute_dictionary["نوع قانون"]
                    law["tabaghe_bandi"] = doc_attribute_dictionary["طبقه بندی"]
                    law["tarikh_sanad_tasvib"] = doc_attribute_dictionary["تاریخ سند تصويب"]
                    law["shomare_sanad_tasvib"] = doc_attribute_dictionary["شماره سند تصویب"]
                    law["shomare_eblagh"] = doc_attribute_dictionary["شماره ابلاغ"]
                    law["tarikh_eblagh"] = doc_attribute_dictionary["تاریخ ابلاغ"]
                    law["marjae_eblagh"] = doc_attribute_dictionary["مرجع ابلاغ"]
                    law["tarikh_ejra"] = doc_attribute_dictionary["تاريخ اجرا"]
                    law["akharin_vaziat"] = doc_attribute_dictionary["آخرین وضعیت"]
                    law["dastgah_mojri"] = "_".join(mojri_list)
                    law["ronevesht"] = "_".join(ronevesht_list)


                    temp.noe_ghanon = law["noe_ghanon"]
                    temp.tabaghe_bandi = law["tabaghe_bandi"]
                    temp.tarikh_sanad_tasvib = law["tarikh_sanad_tasvib"]
                    temp.shomare_sanad_tasvib = law["shomare_sanad_tasvib"]
                    temp.shomare_eblagh = law["shomare_eblagh"]
                    temp.tarikh_eblagh = law["tarikh_eblagh"]
                    temp.marjae_eblagh = law["marjae_eblagh"]
                    temp.tarikh_ejra = law["tarikh_ejra"]
                    temp.akharin_vaziat = law["akharin_vaziat"]
                    temp.dastgah_mojri = law["dastgah_mojri"]
                    temp.ronevesht = law["ronevesht"]
                    temp.status = "done" if temp.status == "file" else "detail"
                    temp.save()

                else:
                    temp = Law.objects.filter(pid=id_).exclude(status='done').exclude(status='file')
                    if temp.count() == 0:
                        continue
                    else:
                        temp = temp[0]
                    Text_Page = tup[1]

                    Text_soup = BeautifulSoup(Text_Page, features="html.parser")
                    text = Text_soup.find("div", {"id": "treeText"}).find_all("p")
                    txt = ''
                    for text_ in text:
                        txt += text_.get_text().strip() + '\n'
                    text = txt.strip()
                    if len(text) == 0 or text == "متن این مصوبه هنوز وارد سامانه نشده است لطفا قسمت تصویر را نیز ملاحظه فرمایید.":
                        has_text = '-'
                    else:
                        f = open(f'{base_dir}/files/{temp.name}.txt', "w", encoding="utf-8")
                        for line in text:
                            f.write(line)
                        f.close()
                        has_text = '+'
                    temp.has_text = has_text
                    temp.status = "done" if temp.status == "detail" else "file"
                    temp.save()
        except Exception as e:
            print(f'error:{e}')
            print(f'{tup[0]}')


def fix():
    Excel_file = pd.read_excel('./db_law.xlsx')
    print("Read Excel File: Done")

    for index, row in Excel_file.iterrows():
        print(index)
        Law.objects.create(pid=str(row["pid"]),
                           name=fix_dir_name(str(row["name"]).strip()),
                           approve=str(row["approve"]),
                           data=str(row["data"]),
                           noe_ghanon=str(row["noe_ghanon"]),
                           tabaghe_bandi=str(row["tabaghe_bandi"]),
                           tarikh_sanad_tasvib=str(row["tarikh_sanad_tasvib"]),
                           shomare_sanad_tasvib=str(row["shomare_sanad_tasvib"]),
                           shomare_eblagh=str(row["shomare_eblagh"]),
                           tarikh_eblagh=str(row["tarikh_eblagh"]),
                           marjae_eblagh=str(row["marjae_eblagh"]),
                           tarikh_ejra=str(row["tarikh_ejra"]),
                           akharin_vaziat=str(row["akharin_vaziat"]),
                           dastgah_mojri=str(row["dastgah_mojri"]),
                           ronevesht=str(row["ronevesht"]),
                           status="file")
    files = [f for f in listdir(f'{base_dir}/old_files') if isfile(join(f'{base_dir}/old_files', f))]
    for file_addr in files:
        old_name = base_dir + r'/old_files/' + file_addr
        print(file_addr.replace(".txt", ""))
        try:
            obj = Law.objects.get(pid=file_addr.replace(".txt", ""))
            new_name = base_dir + r'/files/' + obj.name + r'.txt'
            os.rename(old_name, new_name)
            obj.has_text = '+'
            obj.status = 'done'
            obj.save()
        except:
            # obj.has_text = '-'
            # obj.status = 'detail'
            # obj.save()
            continue
        # _file = open(old_name, 'r', encoding="utf-8")
        # lines = _file.readlines()
        # _file.close()
        # _file = open(new_name, 'w', encoding="utf-8")
        # _file.writelines(lines)
        # _file.close()


if __name__ == '__main__':
    make_excel()
    # Law.objects.filter(has_text="").delete()
    # crawl()
    # fix()
    # Excel_file = pd.read_excel('./data.xlsx')
    #
    # for index, row in Excel_file.iterrows():
    #     id__ = str(row["pid"])
    #     if Law.objects.filter(pid=id__, status='done').count() > 0:
    #         continue
    #     Attribute_URL = "https://qavanin.ir/Law/Attribute/" + id__
    #     Text_URL = "https://qavanin.ir/Law/TreeText/" + id__
    #     dl_urls[id__ + "#Attribute_URL"] = Attribute_URL
    #     dl_urls[id__ + "#Text_URL"] = Text_URL
    #     if Law.objects.filter(pid=id__).count() == 0:
    #         Law.objects.create(pid=id__, name=fix_dir_name(str(row["name"]).strip()), approve=str(row["approval"]),
    #                            data=str(row["date"]), status='empty')
    #     if len(dl_urls.keys()) >= 200:
    #         multi_request(dl_urls)
    #         print(f'loaded {index + 1} laws.')
    #         dl_urls = {}
    # Law.objects.filter(status='file').update(status='detail')
    # for law in
    #     law.name = fix_dir_name(law.name.strip())
    #     law.save()
    # rename_files()
    # pass
