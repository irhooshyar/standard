from abdal import config
from pathlib import Path
from scripts.English import Preprocessing
from en_doc.models import Document
import math
from itertools import chain
import time
import threading
def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list

def Docs_List_Extractor(docs_list, Country, Result_Create_List, thread_number):

    Create_List = []
    for file in docs_list:
        doc_obj = Document(name=file, country_id=Country)
        Create_List.append(doc_obj)

    Result_Create_List[thread_number] = Create_List

def apply(folder_name, Country):
    t = time.time()
    Document.objects.filter(country_id=Country).delete()

    dataPath = str(Path(config.DATA_PATH, folder_name))
    all_files = Preprocessing.readFiles(dataPath, readContent=False)
    all_files = sorted(all_files.keys())

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    Sliced_Files = Slice_List(all_files, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in Sliced_Files:
        thread = threading.Thread(target=Docs_List_Extractor,
                                  args=(S, Country, Result_Create_List, thread_number,))
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
        Document.objects.bulk_create(sub_list)

    print("time ", time.time() - t)
