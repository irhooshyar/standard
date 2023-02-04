from scripts.Persian import Preprocessing
from doc.models import Document, DocumentParagraphs
import math
from itertools import chain
import time
import threading
from abdal import config

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

def Docs_Text_Extractor(documents_list, Docs_Text_Dict):
    for document in documents_list:
        document_id = document.id
        document_paragraph_list = DocumentParagraphs.objects.filter(document_id=document).values("document_id", "text")
        document_text = ""
        for paragraph in document_paragraph_list:
            document_text += paragraph["text"] + " "
        Docs_Text_Dict[document_id] = document_text


def apply(folder_name, Country):

    t = time.time()

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

    Result_Dictionary = {}

    thread_obj = []
    thread_number = 0
    for S in Docs_Text_Dict_Slices:
        thread = threading.Thread(target=Feature_Extractor, args=(S, Result_Dictionary))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    for doc_id, features in Result_Dictionary.items():
        Document.objects.filter(id=doc_id).update(word_count=features["word_count"], distinct_word_count=features["distinct_word_count"], stopword_count=features["stopword_count"])

    print("time ", time.time() - t)

def Feature_Extractor(input_data, Result_Dictionary):
    for doc_id, doc_text in input_data.items():

        doc_text_preprocessed = Preprocessing.Preprocessing(doc_text, removeSW=False, stem=False)
        total = len(doc_text_preprocessed)
        distinct = len(list(set(doc_text_preprocessed)))
        doc_text_preprocessed = Preprocessing.Preprocessing(doc_text, stem=False)
        stopWords = total - len(doc_text_preprocessed)

        Result_Dictionary[doc_id] = {"word_count": total, "distinct_word_count": distinct, "stopword_count": stopWords}

