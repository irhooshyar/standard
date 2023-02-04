import json
from itertools import chain
from pathlib import Path

from itertools import islice
from abdal import config
from scripts.Persian import Preprocessing
import re
from hazm import *
from en_doc.models import DocumentDefinition, ExtractedKeywords, Document, DocumentParagraphs
import time
import threading
from abdal import config
import math
from itertools import chain

regexes = [
    r'"[^"]+?" means [\s\S]*?[\.;]',
    r'“[^“]+?” means [\s\S]*?[\.;]',
    r'"[^"]+?" \(.*?\) means [\s\S]*?[\.;]',
    r'“[^“]+?” \(.*?\) means [\s\S]*?[\.;]',

    r'"[^"]+?" means—[\s\S]*?\.;',
    r'“[^“]+?” means—[\s\S]*?\.',
    r'"[^"]+?" \(.*?\) means—[\s\S]*?\.',
    r'“[^“]+?” \(.*?\) means—[\s\S]*?\.',

    r'“[^“]+?” has the meaning [\s\S]*?[\.;]',
    r'"[^"]+?" has the meaning [\s\S]*?[\.;]',
    r'“[^“]+?” \(.*?\) has the meaning [\s\S]*?[\.;]',
    r'"[^"]+?" \(.*?\) has the meaning [\s\S]*?[\.;]',
]
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
            document_text += paragraph["text"] + "\n"
        Docs_Text_Dict[document_id] = document_text


def apply(folder_name, Country):

    t = time.time()

    documents = Document.objects.filter(country_id=Country)
    old_def = DocumentDefinition.objects.filter(document_id__in=documents)
    ExtractedKeywords.objects.filter(definition_id__in=old_def).delete()
    old_def.delete()

    Docs_Text_Dict = {}

    Thread_Count = config.Thread_Count
    document_list_Slices = Slice_List(documents, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in document_list_Slices:
        thread = threading.Thread(target=Docs_Text_Extractor, args=(S, Docs_Text_Dict,))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Extracted_Create_list = {}
    Definition_Result_Create_List = [None] * Thread_Count

    thread_obj = []
    thread_number = 0
    for S in document_list_Slices:
        thread = threading.Thread(target=extract_definition, args=(S, Docs_Text_Dict, Extracted_Create_list, Definition_Result_Create_List, thread_number))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Definition_Result_Create_List))

    batch_size = 20000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentDefinition.objects.bulk_create(sub_list)

    temp_list = []
    for doc, key_list in Extracted_Create_list.items():
        definition_obj = DocumentDefinition.objects.get(document_id=doc)
        for keyword in key_list:
            extracted_obj = ExtractedKeywords(word=keyword, definition_id=definition_obj)
            temp_list.append(extracted_obj)

        if temp_list.__len__() > batch_size:
            ExtractedKeywords.objects.bulk_create(temp_list)
            temp_list = []
    ExtractedKeywords.objects.bulk_create(temp_list)

    print("time ", time.time() - t)


def extract_definition(documents, Docs_Text_Dict, Extracted_Create_list, Definition_ResultCreate_List, thread_number):
    Definition_Create_list = []
    for doc in documents:

        keywords = []
        doc_text = Docs_Text_Dict[doc.id]
        definition = ""

        for regex in regexes:
            pair = re.compile(regex)
            search = pair.findall(doc_text)
            for search_ in search:
                if "means" in search_:
                    keyword = search_.split("means")[0]
                else:
                    keyword = search_.split("has the meaning")[0]

                if keyword != "" and len(keyword) < 1000:
                    keywords.append(keyword.replace("“"," ").replace("”"," ").replace('"'," ").strip())

            definition += "".join(x.replace("\n"," ") + "\n\n" for x in search)

        if definition.replace(" ", "") != "":
            definition_obj = DocumentDefinition(text=definition, document_id=doc)
            Definition_Create_list.append(definition_obj)

            for keyword in keywords:
                if doc not in Extracted_Create_list:
                    Extracted_Create_list[doc] = [keyword.strip()]
                else:
                    Extracted_Create_list[doc].append(keyword.strip())

    Definition_ResultCreate_List[thread_number] = Definition_Create_list