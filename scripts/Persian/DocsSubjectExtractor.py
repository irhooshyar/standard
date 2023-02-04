import operator
from doc.models import DocumentSubject, SubjectKeyWords, Subject, Document, DocumentSubjectKeywords, DocumentParagraphs, Measure
from django.db.models import Count, Q, Value

from django.db.models.functions import Concat
import math
from itertools import chain
import time
import threading
from abdal import config

def normalize_dict(subject_dict):
    if (sum(subject_dict.values())) == 0:
        factor = 0
    else:
        factor = 1.0 / sum(subject_dict.values())

    for k in subject_dict:
        subject_dict[k] = round(subject_dict[k] * factor, 2)

    return subject_dict

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
        document_name = document.name
        document_id = document.id
        document_approval = document.approval_reference_name

        document_paragraph_list = DocumentParagraphs.objects.filter(document_id=document).values("document_id", "text")
        document_text = ""
        for paragraph in document_paragraph_list:
            document_text += paragraph["text"] + " "

        Docs_Text_Dict[(document_name, document_id, document_approval)] = document_text

def Docs_Subject_Keywords_Extractor(Sub_Docs_Text_Dict, Subject_Keyword_Dict, Result_Create_List, thread_number, Document_Subject_Score):
    Create_List = []
    o = 1
    for (doc_name, doc_id, doc_approval), doc_text in Sub_Docs_Text_Dict.items():
        subject_dictionary = {}
        for (subject_name, subject_id), [text_title_keyword_list, approval_keyword_list] in Subject_Keyword_Dict.items():
            subject_word_score_count = 0
            for keyword in text_title_keyword_list:
                keyword_text = " " + keyword["word"] + " "
                keyword_id = keyword["id"]

                title_count = doc_name.count(keyword_text)
                if title_count > 0:
                    keyword_place = "عنوان"
                    doc_sub_key_obj = DocumentSubjectKeywords(document_id_id=doc_id, subject_keyword_id_id=keyword_id, count=title_count, place=keyword_place)
                    Create_List.append(doc_sub_key_obj)
                    subject_word_score_count += 1

                text_count = doc_text.count(keyword_text)
                if text_count > 0:
                    keyword_place = "متن"
                    doc_sub_key_obj = DocumentSubjectKeywords(document_id_id=doc_id, subject_keyword_id_id=keyword_id, count=text_count, place=keyword_place)
                    Create_List.append(doc_sub_key_obj)
                    subject_word_score_count += 20

            for keyword in approval_keyword_list:
                keyword_text = keyword["word"]
                keyword_id = keyword["id"]
                if doc_approval == keyword_text:
                    keyword_place = "مرجع تصویب"
                    doc_sub_key_obj = DocumentSubjectKeywords(document_id_id=doc_id, subject_keyword_id_id=keyword_id, count=1, place=keyword_place)
                    Create_List.append(doc_sub_key_obj)
                    subject_word_score_count += 1

            subject_dictionary[subject_id] = subject_word_score_count

        Document_Subject_Score[doc_id] = subject_dictionary

    Result_Create_List[thread_number] = Create_List

def apply(folder_name, Country):

    t = time.time()

    Document.objects.filter(country_id=Country).update(subject_id=None)
    DocumentSubjectKeywords.objects.filter(document_id__country_id=Country).delete()
    DocumentSubject.objects.filter(document_id__country_id=Country).delete()

    Subject_Keyword_Dict = {}
    subject_list = Subject.objects.all()

    Subject_Name_Dict = {}

    for subject in subject_list:
        subject_name = subject.name
        subject_id = subject.id

        Subject_Name_Dict[subject_id] = subject_name

        text_title_keyword_list = SubjectKeyWords.objects.filter(subject_id=subject, place="متن و عنوان").values("id", 'word')
        approval_keyword_list = SubjectKeyWords.objects.filter(subject_id=subject, place="مرجع تصویب" ).values("id", 'word')

        Subject_Keyword_Dict[(subject_name, subject_id)] = [text_title_keyword_list, approval_keyword_list]

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

    Result_Create_List = [None] * Thread_Count
    Document_Subject_Score = {}

    thread_obj = []
    thread_number = 0
    for S in Docs_Text_Dict_Slices:
        thread = threading.Thread(target=Docs_Subject_Keywords_Extractor, args=(S, Subject_Keyword_Dict, Result_Create_List, thread_number, Document_Subject_Score))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    Result_Create_List = list(chain.from_iterable(Result_Create_List))

    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentSubjectKeywords.objects.bulk_create(sub_list)

    Ekhtesasi_id = Subject.objects.get(name="اختصاصی-تخصصی").id
    Measure_Similarity = Measure.objects.get(english_name="JaccardSimilarity")
    Result_Create_List = []
    for document_id, subject_score_dict in Document_Subject_Score.items():
        if subject_score_dict[Ekhtesasi_id] > 0:
            subject_score_dict.pop(Ekhtesasi_id, None)
            subject_score_dict = normalize_dict(subject_score_dict)
            subject_score_dict[Ekhtesasi_id] = 1
            subject_name = Subject_Name_Dict[Ekhtesasi_id]
            Document.objects.filter(id=document_id).update(subject_id_id=Ekhtesasi_id, subject_name=subject_name, subject_weight=1)
        else:
            subject_score_dict = normalize_dict(subject_score_dict)
            subject_score_dict = dict(sorted(subject_score_dict.items(), key=operator.itemgetter(1), reverse=True))
            doc_subject_id = list(subject_score_dict.keys())[0]
            doc_subject_weight = subject_score_dict[doc_subject_id]
            if subject_score_dict[doc_subject_id] > 0:
                subject_name = Subject_Name_Dict[doc_subject_id]
                Document.objects.filter(id=document_id).update(subject_id_id=doc_subject_id, subject_name=subject_name, subject_weight=doc_subject_weight)

        for subject_id, score in subject_score_dict.items():
            doc_sub_obj = DocumentSubject(document_id_id=document_id, subject_id_id=subject_id, measure_id=Measure_Similarity, weight=score)
            Result_Create_List.append(doc_sub_obj)

    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentSubject.objects.bulk_create(sub_list)

    print("time ", time.time() - t)








