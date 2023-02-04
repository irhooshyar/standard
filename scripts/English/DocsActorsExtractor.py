from abdal import config
from en_doc.models import DocumentActor, DocumentParagraphs, Actor
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


def apply(folder_name, Country):

    t = time.time()

    DocumentActor.objects.filter(document_id__country_id=Country).delete()

    Actors_List = Actor.objects.all()

    Document_Paragraphs_List = DocumentParagraphs.objects.filter(document_id__country_id=Country).values("id", "document_id", "text")

    Thread_Count = config.Thread_Count

    Sliced_Files = Slice_List(Document_Paragraphs_List, Thread_Count)

    index = 1
    for file in Sliced_Files:
        print(index)
        index += 1
        sub_Sliced_Files = Slice_List(file, Thread_Count)
        Result_Create_List = [None] * Thread_Count
        thread_obj = []
        thread_number = 0
        for S in sub_Sliced_Files:
            thread = threading.Thread(target=ExtractActors,
                                      args=(S, Actors_List, Result_Create_List, thread_number,))
            thread_obj.append(thread)
            thread_number += 1
            thread.start()
        for thread in thread_obj:
            thread.join()

        Result_Create_List = list(chain.from_iterable(Result_Create_List))

        print(Result_Create_List.__len__())

        batch_size = 50000
        slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
        for i in range(slice_count):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
            sub_list = Result_Create_List[start_idx:end_idx]
            DocumentActor.objects.bulk_create(sub_list)

    print("time ", time.time() - t)


def ExtractActors(input_data, Actors_List, Result_Create_List, thread_number):
    CreateList = []
    for actor in Actors_List:
        actor_id = actor.id
        actor_name = actor.name
        for paragraph in input_data:
            paragraph_id = paragraph["id"]
            paragraph_text = paragraph["text"]
            paragraph_document_id = paragraph["document_id"]
            if " " + actor_name + " " in paragraph_text:
                actor_doc_obj = DocumentActor(document_id_id=paragraph_document_id, paragraph_id_id=paragraph_id, actor_id_id=actor_id)
                CreateList.append(actor_doc_obj)
    Result_Create_List[thread_number] = CreateList
