from abdal import config
from doc.models import DocumentKeywords, Document, KeywordList, DocumentParagraphs
from django.db.models import Count, Q
import math
from itertools import chain
import time
import threading
from abdal import config

def Docs_Text_Extractor(documents_list, Docs_Text_Dict):
    for document in documents_list:
        document_name = document.name
        document_id = document.id
        document_paragraph_list = DocumentParagraphs.objects.filter(document_id=document).values("document_id", "text")
        document_text = ""
        for paragraph in document_paragraph_list:
            document_text += paragraph["text"] + " "
        Docs_Text_Dict[(document_name, document_id)] = document_text

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

    DocumentKeywords.objects.filter(document_id__country_id=Country).delete()
    key_list = KeywordList.objects.all()

    Docs_Text_Dict = {}
    document_list = Document.objects.filter(country_id=Country)[:5000]
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
        thread = threading.Thread(target=Docs_KeyWord_Extractor, args=(S, key_list, Result_Create_List, thread_number))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))

    batch_size = 20000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentKeywords.objects.bulk_create(sub_list)

    print("time ", time.time() - t)


def Docs_KeyWord_Extractor(Docs_Text_Dict, key_list, Result_Create_List, thread_number):
    Create_List = []
    for (doc_name, doc_id), doc_text in Docs_Text_Dict.items():
        for keyword in key_list:
            keyword_word = keyword.word
            if " " + keyword_word + " " in doc_text:
                keyword_count = doc_text.count(" " + keyword_word + " ")
                doc_key_obj = DocumentKeywords(document_id_id=doc_id, keyword_id=keyword, count=keyword_count)
                Create_List.append(doc_key_obj)
    Result_Create_List[thread_number] = Create_List
