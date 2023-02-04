from pathlib import Path
from abdal import config
from scripts.Persian import Preprocessing
from doc.models import Document,DocumentParagraphs
import math
import threading
from itertools import chain
import time


def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


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

    dataPath = str(Path(config.DATA_PATH, folder_name))
    DocumentParagraphs.objects.filter(document_id__country_id=Country).delete()
    files_text = Preprocessing.readFiles(dataPath, preprocess=False)

    Thread_Count = config.Thread_Count
    Result_Create_List = [None] * Thread_Count
    Sliced_Files = Slice_Dict(files_text, Thread_Count)

    document = Document.objects.filter(country_id=Country)
    Document_Dictionary = {}
    for doc in document:
        Document_Dictionary[doc.file_name] = doc.id

    thread_obj = []
    thread_number = 0
    for S in Sliced_Files:
        thread = threading.Thread(target=Extract_Paragraph, args=(S, Document_Dictionary, Result_Create_List, thread_number,))
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
        DocumentParagraphs.objects.bulk_create(sub_list)

    print("time ", time.time() - t)

def delete_empty_line(line_list):
    result_line = []
    for line in line_list:
        if len(line.replace(" ", "").replace("\t", "")) > 10:
            result_line.append(line.replace("\t", "").replace("  ", " "))
    return result_line


def Extract_Paragraph(files_text, Document_Dictionary, Result_Create_List, thread_number,):
    Create_List = []
    f = 0
    for key, value in files_text.items():
        f += 1
        paragraphs = value.split("\n")
        # paragraphs = value.split(".\n")
        paragraphs = delete_empty_line(paragraphs)
        document = Document_Dictionary[key]
        for i in range(paragraphs.__len__()):
            paragraph = arabic_preprocessing(paragraphs[i])

            # added for standard
            # paragraph = paragraph.replace('\n',' ')

            # while '  ' in paragraph:
            #     paragraph = paragraph.replace('  ', ' ')
            # -----------------------------------------------
            doc_par = DocumentParagraphs(document_id_id=document, text=paragraph, number=i)
            Create_List.append(doc_par)

    Result_Create_List[thread_number] = Create_List
