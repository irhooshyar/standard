import json
from pathlib import Path
from abdal import config
from scripts.English import Preprocessing
from en_doc.models import DocumentWords, Document
from collections import Counter
import math
import threading
from itertools import chain
import time

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

    DocumentWords.objects.filter(country_id=Country).delete()

    t = time.time()

    dataPath = str(Path(config.DATA_PATH, folder_name))

    DocWordsDict = Preprocessing.readFiles_parallel(dataPath, preprocessArg={"stem": False})

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    DocWordsDict_Sliced = Slice_Dict(DocWordsDict, Thread_Count)

    document = Document.objects.filter(country_id=Country)
    Document_Dictionary = {}
    for doc in document:
        Document_Dictionary[doc.name] = doc.id

    thread_obj = []
    thread_number = 0
    for S in DocWordsDict_Sliced:
        thread = threading.Thread(target=Extracted_inverted, args=(S, Document_Dictionary, Result_Create_List, thread_number, Country,))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))

    batch_size = 50000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentWords.objects.bulk_create(sub_list)

    print("time ", time.time() - t)

def Extracted_inverted(DocWordsDict, Document_Dictionary, Result_Create_List, thread_number, Country):
    place = "متن"
    Create_List = []
    for doc_name, words_list in DocWordsDict.items():
        document_id = Document_Dictionary[doc_name]
        words_list_dict = dict(Counter(words_list))
        for word, count in words_list_dict.items():
            doc_obj = DocumentWords(document_id_id=document_id, country_id=Country, word=word, count=count, place=place, gram=1)
            Create_List.append(doc_obj)

    Result_Create_List[thread_number] = Create_List
