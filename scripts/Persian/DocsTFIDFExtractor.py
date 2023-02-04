from abdal import config
from scripts.Persian import Preprocessing
import math
import os
from pathlib import Path
from doc.models import CountryTFIDFWords, DocumentTFIDF,Document, TFIDFWeight
import math
import threading
from itertools import chain
import time
import heapq
from operator import itemgetter

selected_country_lang = None

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

def Calculate_Words_Document(data_dict):
    words_document_dict = {}
    for doc, word_list in data_dict.items():
        for word in word_list:
            if word not in words_document_dict:
                words_document_dict[word] = [doc]
            else:
                words_document_dict[word].append(doc)
    return words_document_dict

def Calculate_words_Frequency_inDoc(word_list):
    words_frequency_dict = {}
    for word in word_list:
        if word not in words_frequency_dict:
            words_frequency_dict[word] = 1
        else:
            words_frequency_dict[word] += 1
    return words_frequency_dict

def Extract_TF_Object(doc_name, words_frequency_dict, Document_Dictionary):
    global selected_country_lang
    
    doc_name = str(os.path.basename(doc_name))
    doc_id = Document_Dictionary[doc_name]
    Create_List = []

    sum_value = sum(words_frequency_dict.values())
    if selected_country_lang in ["کتاب","استاندارد"] :
        topitems = heapq.nlargest(1000000, words_frequency_dict.items(), key=itemgetter(1))
    else:
        topitems = heapq.nlargest(10, words_frequency_dict.items(), key=itemgetter(1))
    words_frequency_dict_sorted = dict(topitems)

    for word, term_frequency in words_frequency_dict_sorted.items():
        round_weight = round((term_frequency / sum_value)*100, 2)
        doc_tfidf_obj = DocumentTFIDF(word=word, count=term_frequency, weight=round_weight, document_id_id=doc_id)
        Create_List.append(doc_tfidf_obj)

    return Create_List

def apply(folder_name, Country):
    global selected_country_lang
    selected_country_lang = Country.language

    t = time.time()

    DocumentTFIDF.objects.filter(document_id__country_id=Country).delete()
    TFIDFWeight.objects.filter(document_id__country_id=Country).delete()
    CountryTFIDFWords.objects.filter(country=Country).delete()
    
    dataPath = str(Path(config.DATA_PATH, folder_name))

    input_data = Preprocessing.readFiles(dataPath, preprocessArg={"stem": False})

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    Sliced_Files = Slice_Dict(input_data, Thread_Count)

    document = Document.objects.filter(country_id=Country)
    Document_Dictionary = {}
    for doc in document:
        Document_Dictionary[doc.file_name] = doc.id

    thread_obj = []
    thread_number = 0
    for S in Sliced_Files:
        thread = threading.Thread(target=ExtractTfIDF, args=(S, Result_Create_List, Document_Dictionary, thread_number,))
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
        DocumentTFIDF.objects.bulk_create(sub_list)

    print("time ", time.time() - t)
    if selected_country_lang in ["کتاب","استاندارد"]:
        CreateDocumentTFIDF(Country)


def CreateDocumentTFIDF(Country):
    words = DocumentTFIDF.objects.filter(document_id__country_id=Country).values_list('word', flat=True).distinct()
    docs = Document.objects.filter(country_id=Country)
    
    create_TFIDF_weight_doc=[]
    
    for doc in docs:
        words_dict = {}
        for word in words:
            words_dict[word] = 0
        doc_words = DocumentTFIDF.objects.filter(document_id=doc.id)
        for word in doc_words:
            words_dict[word.word] = word.weight

        
        weight_str = ""
        doc_id = Document.objects.get(id=doc.id)
        for word in words_dict.keys():
            weight_str += str(words_dict[word]) + "--"
        obj = TFIDFWeight(document=doc_id, weights=weight_str ) 
        create_TFIDF_weight_doc.append(obj) 
        
    words_str = ""
    for word in words:
        words_str += str(word) + "--"  
    TFIDFWeight.objects.bulk_create(create_TFIDF_weight_doc)
    CountryTFIDFWords.objects.create(country=Country, words=words_str)
            

def ExtractTfIDF(input_data, Result_Create_List, Document_Dictionary, thread_number):
    results = []
    for doc, wordList in input_data.items():
        words_frequency_dict = Calculate_words_Frequency_inDoc(wordList)
        Object_List = Extract_TF_Object(doc, words_frequency_dict, Document_Dictionary)
        results += Object_List
    Result_Create_List[thread_number] = results
