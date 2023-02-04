import math
from itertools import chain
import time
import threading
from abdal import config
from scripts.Persian import Preprocessing
import re
from hazm import *
from doc.models import DocumentGeneralDefinition, Document, DocumentParagraphs

normalizer = Normalizer()

def Docs_Text_Extractor(documents_list, Docs_Text_Dict):
    for document in documents_list:
        document_id = document.id
        document_paragraph_list = DocumentParagraphs.objects.filter(document_id=document).values("document_id", "text", "id").order_by("number")
        document_text = {}
        for paragraph in document_paragraph_list:
            paragraph_id = paragraph["id"]
            document_text[paragraph_id] = paragraph["text"]
        Docs_Text_Dict[document_id] = document_text


def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list

def Slice_Dict(docs_dict, n):
    results = []

    docs_dict_keys = list(docs_dict.keys())
    step = math.ceil(docs_dict.keys().__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_dict_keys.__len__())
        res = {}
        for j in range(start_idx, end_idx):
            key = docs_dict_keys[j]
            res[key] = docs_dict[key]
        results.append(res)

    return results

def apply(folder_name, Country):

    t = time.time()

    DocumentGeneralDefinition.objects.filter(document_id__country_id=Country).delete()

    Docs_Text_Dict = {}
    document_list = Document.objects.filter(country_id=Country)
    Thread_Count = config.Thread_Count
    document_list_Slices = Slice_List(document_list, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in document_list_Slices:
        thread = threading.Thread(target=Docs_Text_Extractor, args=(S, Docs_Text_Dict,))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Docs_Text_Dict_Slices = Slice_Dict(Docs_Text_Dict, Thread_Count)

    Result_Create_List = [None] * Thread_Count

    thread_obj = []
    thread_number = 0
    for S in Docs_Text_Dict_Slices:
        thread = threading.Thread(target=General_Definition_Extractor, args=(S, Result_Create_List, thread_number))
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
        DocumentGeneralDefinition.objects.bulk_create(sub_list)

    print("time ", time.time() - t)

def General_Definition_Extractor(input_data_dict, Result_Create_List, thread_number,): # input_data_dict is a Dic<document_id,Dic<paragraph_id,text>> , Result_Create_List = [thread_count]

    ignore_list = ["سوم", "اولاً", "ثانیاً", "استعلام", "سؤال", "موضوع", "از قبیل", "از جمله", "مرحله", "پیوست", "تبصره", "ماده", "اصل", "تاریخ", "عبارتند از", "بخش", "فصل", "شماره", "لطفا بفرمایید", "تعاریف و اصطلاحات", "چنین رای داده شده است"]  

    Create_List = []

    for document_id, document_text in input_data_dict.items():
        for paragraph_id, paragraph_text in document_text.items():

            char_index = paragraph_text.find(":")

            if 0 <= char_index < (paragraph_text.__len__() / 1.5):

                word = paragraph_text[0: char_index].strip() # Trim() C# (قانون)
                definition = paragraph_text[char_index+1:]

                #definition_processing
                try:
                    definition = definition.split("شماره ویژه نامه")[0].strip()
                except:
                    pass
                if (len(definition) > 2100):
                    continue
                if ("......................." in definition):
                    continue
                definition = definition.strip()
                definition = definition.strip("-")
                definition = definition.strip("–")
                definition = definition.strip("\u200c")

                #word_processing
                word = word[max(word.rfind("-")+1, 0):] # rfind : reverse find
                word = word[max(word.rfind("–")+1, 0):] 
                word = word[max(word.rfind("ـ")+1, 0):]
                word = word[max(word.rfind("_")+1, 0):]
                word = word[max(word.rfind(".")+1, 0):]
                word = word[max(word.rfind("•")+1, 0):].strip().strip("\u200c").strip("\u200F")
                # char)  {و ) , الف ) ,  18)‌ }
                # (/ب مورخ) , {‌الف ) } starts with &zwnj , ()
                regexes = [
                    r'^[0-9]+\s?[)](\u200c)? ', # '[0-9]+[)] ?'
                    r'^[\u06F0-\u06F90-9]+\s?[)](\u200c)? ', # persian numbers
                    r'^الف\s[)](\u200c)?', # ^ starts with
                    r'^[\u0600-\u06FF]\s[)](\u200c)?', # الف-ی
                    r'^الف\s', 
                    r'^[\u0600-\u06FF]\s', # الف-ی
                ]
                for regex in regexes:
                    pair = re.compile(regex)
                    search = pair.findall(word)
                    for search_ in search:
                        word = word[max(word.rfind(search_) + len(search_), 0):].strip().strip("\u200c")
                # word = word.strip("\u200c")
                word = word.strip(" ‌ـ‌  ")
                word = word.strip(" ‌")
                word = word.strip(" ")
                word = word.strip("‌")
                word = word.strip("\u200c").strip("\u200F")

                if len(word) <= 5 or len(word) > 50 or any(x in word for x in ignore_list):
                    continue
                
                # dash in begining of definition
                isAbrev = False
                # if definition.find(word) > 0 :
                if 0 < definition.find(word) < 2 :
                    isAbrev = True

                doc_def_obj = DocumentGeneralDefinition(document_id_id=document_id, keyword=word, text=definition, is_abbreviation = isAbrev)
                Create_List.append(doc_def_obj)

    Result_Create_List[thread_number] = Create_List


