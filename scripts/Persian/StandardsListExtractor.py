from pydoc import doc
from unicodedata import name
from abdal import config
from pathlib import Path
from scripts.Persian import Preprocessing
from doc.models import Document, Standard, Standard_Branch, Standard_Status
import pandas as pd
import math
from itertools import chain
import time
import threading

def standardFileName(name):
    name = name.replace(".", "")
    name = arabicCharConvert(name)
    name = persianNumConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  "," ")

    return name

def persianNumConvert(text):
    persian_num_dict = {"۱": "1" ,"۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹":"9" , "۰": "0" }
    for key, value in persian_num_dict.items():
        text = text.replace(key, value)
    return text

def arabicCharConvert(text):
    arabic_char_dict = {"ى": "ی" ,"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ":" ", "\n\n":"\n", "\n ":"\n" , }
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)

    return text

def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text

def numbers_preprocessing(text):
  persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
  arabicNumbers  = ['٠','١', '٢', '٣','٤', '٥', '٦','٧', '٨', '٩']
  for c in persianNumbers:
    text = text.replace(c, str(ord(c)-1776))
  for c in arabicNumbers:
    text = text.replace(c, str(ord(c)-1632))
  return text

def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)
    text = numbers_preprocessing(text)

    return text

def DataFrame2Dict(df, key_field, values_field):
    result_dict = {}
    for index, row in df.iterrows():
        data_list = {}
        for field in values_field:
            data_list[field] = row[field]
        result_dict[row[key_field]] = data_list

    return result_dict

def apply(folder_name, Country):
    t = time.time()

    excelFile = str(Path(config.PERSIAN_PATH, 'Standard.xlsx'))
    df = pd.read_excel(excelFile)
    df['subject'] = df['subject'].apply(lambda x: standardFileName(x))
    df = df.drop_duplicates(subset=['subject'])

    dataframe_dictionary = DataFrame2Dict(df, "standard_number", ["subject",'approval_year','ICS'])

    dataPath = str(Path(config.DATA_PATH, folder_name))
    all_files = Preprocessing.readFiles(dataPath, readContent=False)
    all_files = list(set(all_files.keys()))

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    Sliced_Files = Slice_List(all_files, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in Sliced_Files:
        thread = threading.Thread(target=Docs_List_Extractor, args=(S, Country, dataframe_dictionary, Result_Create_List, thread_number,))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))
    batch_size = 5000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)


    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        Document.objects.bulk_create(sub_list)


    # docs = Document.objects.filter(file_name__in=dataframe_dictionary.keys())
    docs = Document.objects.filter(country_id=Country)

    sta_create_List = []
    for doc in docs:
        standard_number = doc.file_name
        sta_values = None
        try:
            sta_values = dataframe_dictionary.get(str(standard_number))
        except:
            try:
                sta_values = dataframe_dictionary.get(int(standard_number))
            except:
                pass

        if not sta_values:
            subject = str(standard_number)
            approval_year = None
            ICS = None
        else:
            subject = sta_values['subject']
            approval_year = sta_values['approval_year']
            ICS = sta_values['ICS']

        sta_obj = Standard(standard_number=standard_number,
            document_id=doc,
            subject=subject,
            approval_year=approval_year,
            ICS=ICS,
        )
        doc.name = subject
        sta_create_List.append(sta_obj)

    Document.objects.bulk_update(docs, ['name'])
    Standard.objects.bulk_create(sta_create_List)

    print("time ", time.time() - t)

def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list

def Docs_List_Extractor(docs_list, Country, dataframe_dictionary, Result_Create_List, thread_number):

    Create_List = []
    idx = 0
    for file in docs_list:
        idx += 1
        if file in dataframe_dictionary:
            subject = dataframe_dictionary[file]['subject']
            doc_obj = Document(name=subject, file_name=file, country_id=Country)
            Create_List.append(doc_obj)
        else:
            doc_obj = Document(name='نامشخص' + '(' + file + ')', file_name=file, country_id=Country)
            Create_List.append(doc_obj)
        

    Result_Create_List[thread_number] = Create_List
