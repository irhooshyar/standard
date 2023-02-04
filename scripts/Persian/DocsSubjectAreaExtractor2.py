import operator
from doc.models import DocumentSubject, SubjectKeyWords, Subject, Document, DocumentSubjectKeywords, DocumentParagraphs, \
    Measure, DocumentSubjectSubAreaKeywords, DocumentSubjectSubArea, SubjectSubArea, SubjectSubAreaKeyWords
from django.db.models import Count, Q, Value

from django.db.models.functions import Concat
import math
from itertools import chain
import time
import threading
from abdal import config, es_config
from elasticsearch import Elasticsearch
es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)

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

        # document_paragraph_list = DocumentParagraphs.objects.filter(
        #     document_id=document).values("document_id", "text")
        document_text = ""
        # for paragraph in document_paragraph_list:
        #     document_text += paragraph["text"] + " "

        Docs_Text_Dict[(document_name, document_id,
                        document_approval)] = document_text


def Docs_Subject_Keywords_Extractor(Sub_Docs_Text_Dict, Subject_Keyword_Dict, Result_Create_List, thread_number, Document_Subject_Score):
    Create_List = []

    for (doc_name, doc_id, doc_approval), doc_text in Sub_Docs_Text_Dict.items():
        subject_dictionary = {}

        for (subject_name, subject_id), text_title_keyword_list in Subject_Keyword_Dict.items():
            
            subject_word_score_count = 0

            res_query = {"bool": {
                "filter": 
                    {
                        "term": {
                            "document_id": doc_id
                        }
                    }
                ,
                "should":[]
            }}
            
            for keyword in text_title_keyword_list:
                
                # keyword_text = " " + keyword["word"] + " "
                # keyword_id = keyword["id"]

                # title_count = doc_name.count(keyword_text)
                # if title_count > 0:
                #     keyword_place = "عنوان"
                #     doc_sub_key_obj = DocumentSubjectSubAreaKeywords(document_id_id=doc_id, subject_sub_area_keyword_id_id=keyword_id, count=title_count, place=keyword_place)
                #     Create_List.append(doc_sub_key_obj)

                # text_count = doc_text.count(keyword_text)
                # if text_count > 0:
                #     keyword_place = "متن"
                #     doc_sub_key_obj = DocumentSubjectSubAreaKeywords(document_id_id=doc_id, subject_sub_area_keyword_id_id=keyword_id, count=text_count, place=keyword_place)
                #     Create_List.append(doc_sub_key_obj)

                # ---- ES Search ----------------------------------------------------
                keyword_text = keyword["word"]
                title_query = {
                    "match_phrase": {
                        "name":{
                            "query":keyword_text,
                            "boost":5
                        }
                    }
                }

                content_query = {
                    "match_phrase": {
                       "attachment.content":keyword_text
                    }
                }
                res_query["bool"]["should"].append(title_query)
                res_query["bool"]["should"].append(content_query)



            response = client.search(index=es_config.DOTIC_DOC_INDEX,
            _source_includes = ['document_id'],
            request_timeout=40,
            query=res_query,
            size=1)

            result_docs = response['hits']['hits']
            if len(result_docs) > 0:
                subject_word_score_count += response['hits']['hits'][0]['_score']

 
            subject_dictionary[subject_id] = subject_word_score_count

        Document_Subject_Score[doc_id] = subject_dictionary

    Result_Create_List[thread_number] = Create_List


def apply(folder_name, Country):

    t = time.time()

    Document.objects.filter(country_id=Country).update(subject_area_id=None, subject_area_name=None,
                                                       subject_sub_area_id=None, subject_sub_area_name=None)
    DocumentSubjectSubAreaKeywords.objects.filter(
        document_id__country_id=Country).delete()
    DocumentSubjectSubArea.objects.filter(
        document_id__country_id=Country).delete()

    Subject_Keyword_Dict = {}
    subject_list = SubjectSubArea.objects.filter(subject_area_id__language=Country.language).values(
        'name', 'id', 'subject_area_id__id', 'subject_area_id__name')

    sub_area_to_area_dict = {}
    for subject in subject_list:
        sub_area_to_area_dict[subject['id']] = (
            subject['subject_area_id__id'], subject['subject_area_id__name'])

    Subject_Name_Dict = {}

    for subject in subject_list:
        subject_name = subject['name']
        subject_id = subject['id']

        Subject_Name_Dict[subject_id] = subject_name

        text_title_keyword_list = SubjectSubAreaKeyWords.objects.filter(subject_sub_area_id_id=subject['id'],
                                                                        place="متن و عنوان").values("id", 'word')

        Subject_Keyword_Dict[(subject_name, subject_id)
                             ] = text_title_keyword_list

    Docs_Text_Dict = {}
    document_list = Document.objects.filter(country_id=Country)
    Thread_Count = config.Thread_Count
    document_list_Slices = Slice_List(document_list, Thread_Count)

    thread_obj = []
    thread_number = 0
    for S in document_list_Slices:
        thread = threading.Thread(
            target=Docs_Text_Extractor, args=(S, Docs_Text_Dict,))
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
        thread = threading.Thread(target=Docs_Subject_Keywords_Extractor, args=(
            S, Subject_Keyword_Dict, Result_Create_List, thread_number, Document_Subject_Score))
        thread_obj.append(thread)
        thread_number += 1
        thread.start()
    for thread in thread_obj:
        thread.join()

    # Result_Create_List = list(chain.from_iterable(Result_Create_List))

    # batch_size = 100000
    # slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    # for i in range(slice_count):
    #     start_idx = i * batch_size
    #     end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
    #     sub_list = Result_Create_List[start_idx:end_idx]
    #     DocumentSubjectSubAreaKeywords.objects.bulk_create(sub_list)

    Measure_Similarity = Measure.objects.get(english_name="JaccardSimilarity")
    Result_Create_List = []
    for document_id, subject_score_dict in Document_Subject_Score.items():
        subject_score_dict = normalize_dict(subject_score_dict)
        subject_score_dict = dict(
            sorted(subject_score_dict.items(), key=operator.itemgetter(1), reverse=True))
        doc_subject_id = list(subject_score_dict.keys())[0]
        doc_subject_weight = subject_score_dict[doc_subject_id]
        if subject_score_dict[doc_subject_id] > 0:
            subject_name = Subject_Name_Dict[doc_subject_id]
            Document.objects.filter(id=document_id).update(subject_sub_area_id_id=doc_subject_id,
                                                           subject_sub_area_name=subject_name,
                                                           subject_sub_area_weight=doc_subject_weight,
                                                           subject_area_id_id=sub_area_to_area_dict[
                                                               doc_subject_id][0],
                                                           subject_area_name=sub_area_to_area_dict[doc_subject_id][1])

        for subject_id, score in subject_score_dict.items():
            doc_sub_obj = DocumentSubjectSubArea(document_id_id=document_id, subject_sub_area_id_id=subject_id,
                                                 measure_id=Measure_Similarity, weight=score)
            Result_Create_List.append(doc_sub_obj)

    batch_size = 100000
    slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
        sub_list = Result_Create_List[start_idx:end_idx]
        DocumentSubjectSubArea.objects.bulk_create(sub_list)

    print("time ", time.time() - t)
