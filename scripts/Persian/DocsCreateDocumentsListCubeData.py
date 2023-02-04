import operator
from doc.models import  Document, CUBE_DocumentJsonList
import time
import threading
from abdal import config
import math
from itertools import chain

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

    CUBE_DocumentJsonList.objects.filter(country_id=Country).delete()

    filesList = Document.objects.filter(country_id=Country).order_by('-approval_date')

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    document_list_Slices = Slice_List(filesList, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in document_list_Slices:
        thread = threading.Thread(target=ExtractList_CUBE, args=(S, Result_Create_List, thread_number, Country,))
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
        CUBE_DocumentJsonList.objects.bulk_create(sub_list)

    print("time ", time.time() - t)

def ExtractList_CUBE(filesList,  Result_Create_List, thread_number, Country):

    Create_List = []
    i=1
    for doc in filesList:
        print(i/filesList.__len__())

        id = doc.id
        name = doc.name

        subject = "نامشخص"
        if doc.subject_id != None:
            subject = doc.subject_name

        approval_reference = "نامشخص"
        if doc.approval_reference_id != None:
            approval_reference = doc.approval_reference_name

        approval_date = "نامشخص"
        if doc.approval_date != None:
            approval_date = doc.approval_date

        function = "SelectDocumentFunction(" + str(id) + ")"
        tag = f'<button type="button" class="btn modal_btn" data-bs-toggle="modal" onclick="{function}">انتخاب</button>'

        json_value = {"id": "", "subject": subject, "document_name": name, "approval_reference": approval_reference,
             "approval_date": approval_date, "tag": tag}

        country_doc_json_obj = CUBE_DocumentJsonList(country_id=Country, document_id=doc, json_text=json_value)
        Create_List.append(country_doc_json_obj)

        i += 1

    Result_Create_List[thread_number] = Create_List



