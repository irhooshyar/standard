from doc.models import Document, Type
from datetime import datetime
import math
from itertools import chain
import time
import threading
from abdal import config


def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "", "": ""}
    for key,value in arabic_char.items():
        text = text.replace(key, value)

    return text

def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list

def Type_Extractor(document_list, type_list_name, Result_Update_Dict):
    for document in document_list:
        document_name = Local_preprocessing(str(document.name))
        for type_obj_name in type_list_name:
            if document_name.startswith(type_obj_name.lstrip()):
                Result_Update_Dict[document.id] = {"type_id": type_list_name[type_obj_name], "type_name": type_obj_name}
                break

def apply(folder_name, Country):

    t = time.time()

    #Document.objects.filter(country_id=Country).update(type_id=None, type_name=None)
    type_list = Type.objects.all()
    type_list_name = {}
    for i in type_list:
        type_list_name[Local_preprocessing(str(i.name))] = i

    Result_Update_Dict = {}
    document_list = Document.objects.filter(country_id=Country)
    Thread_Count = config.Thread_Count
    document_list_Slices = Slice_List(document_list, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in document_list_Slices:
        thread = threading.Thread(target=Type_Extractor, args=(S, type_list_name, Result_Update_Dict,))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    for document_id, values in Result_Update_Dict.items():
        Document.objects.filter(id=document_id).update(type_id=values["type_id"], type_name=values["type_name"])

    print("time ", time.time() - t)