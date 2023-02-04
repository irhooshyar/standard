import json
from pathlib import Path
from abdal import config
from scripts.Persian import Preprocessing
from doc.models import Document, DocumentWords
from collections import Counter
import math
import threading
from itertools import chain
import time

def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list

def apply(folder_name, Country):

    t = time.time()

    Document_List = Document.objects.filter(country_id=Country).values("id", "name")

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    DocWordsDict_Sliced = Slice_List(Document_List, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in DocWordsDict_Sliced:
        thread = threading.Thread(target=Extract_Title_inverted, args=(S, Result_Create_List, thread_number, Country,))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))

    batch_size = 10000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentWords.objects.bulk_create(sub_list)

    print("time ", time.time() - t)

def Extract_Title_inverted(Document_List, Result_Create_List, thread_number, Country):
    place = "عنوان"
    i = 0
    Create_List = []
    for document in Document_List:
        document_name = document["name"]
        document_id = document["id"]

        name_words_list = Preprocessing.Preprocessing(document_name)

        words_list_dict = dict(Counter(name_words_list))

        for word, count in words_list_dict.items():
            doc_obj = DocumentWords(document_id_id=document_id, country_id=Country, word=word, count=count, place=place,gram=1)
            Create_List.append(doc_obj)

    Result_Create_List[thread_number] = Create_List