from operator import itemgetter
from doc.models import ParagraphsSubject, SubjectList, SubjectKeywordsList, SubjectsVersion, DocumentParagraphs, SubjectSubjectGraphCube, Document
import heapq
import time
from elasticsearch import Elasticsearch
from abdal import es_config
import after_response
import math
from abdal import config
import threading
from itertools import chain


es_url = es_config.ES_URL
client = Elasticsearch(es_url,timeout = 30)

def NormalizeDocumentScore(Score_Dict):
    sum_value = sum([value for key, value in Score_Dict.items()])
    factor = 1/sum_value if sum_value > 0 else 0
    result_dict = {}
    for key, value in Score_Dict.items():
        result_dict[key] = round(Score_Dict[key] * factor, 3)

    return result_dict


def get_subject_keyword_list():
    subject_keywords_list = SubjectKeywordsList.objects.all()
    result_dictionary = {}
    for row in subject_keywords_list:
        subject_id = row.subject.id
        keyword_score = row.score
        keyword_word = row.word

        if subject_id not in result_dictionary:
            result_dictionary[subject_id] =[[keyword_word, keyword_score]]
        else:
            result_dictionary[subject_id].append([keyword_word, keyword_score])
    return result_dictionary

def Slice_List(docs_list, n):
    result_list = []

    step = math.ceil(docs_list.__len__() / n)
    for i in range(n):
        start_idx = i * step
        end_idx = min(start_idx + step, docs_list.__len__())
        result_list.append(docs_list[start_idx:end_idx])

    return result_list

@after_response.enable
def apply(folder_name, Country):

    Country.status = "Paragraph_subjectExtractor"
    Country.save()

    Version = SubjectsVersion.objects.get(id=13)

    # ParagraphsSubject.objects.filter(country=Country,
    #                                  version=Version).delete()
    #
    # document_list = Document.objects.filter(country_id=Country, type_id_id=2)
    # print(1)
    # paragraph_list = DocumentParagraphs.objects.filter(document_id__in=document_list).values_list("id", flat=True)
    #
    # t = time.time()
    #
    # Thread_Count = config.Thread_Count
    # Result_Create_List = [None] * Thread_Count
    # paragraph_list_sliced = Slice_List(paragraph_list, Thread_Count)
    #
    # subject_keyword_list = get_subject_keyword_list()
    # print(2)
    # thread_obj = []
    # thread_number = 0
    # for Slice in paragraph_list_sliced:
    #     thread = threading.Thread(target=ExtractSubject, args=(Slice, subject_keyword_list, Country, Version, Result_Create_List, thread_number,))
    #     thread_obj.append(thread)
    #     thread_number += 1
    #     thread.start()
    # for thread in thread_obj:
    #     thread.join()
    #
    #
    # Result_Create_List = list(chain.from_iterable(Result_Create_List))
    #
    # batch_size = 5000
    # slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
    # for i in range(slice_count):
    #     start_idx = i * batch_size
    #     end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
    #     sub_list = Result_Create_List[start_idx:end_idx]
    #     ParagraphsSubject.objects.bulk_create(sub_list)
    #
    # print("time ", time.time() - t)
    #
    # Country.status = "SubjectSubjectGraph"
    # Country.save()

    GetSubjectSubjectGraphData(Country.id, Version.id)

    Country.status = "Done"
    Country.save()


def ExtractSubject(paragraph_list, subject_keyword_list, Country, Version, Result_Create_List, thread_number, ):
    paragraphs_score = {}
    i=0
    for paragraph_id in paragraph_list:
        i+=1
        for subject_id, keyword_list in subject_keyword_list.items():
            for [keyword_word, keyword_score] in keyword_list:
                print(i / paragraph_list.__len__())
                content_query = {
                    "bool": {
                        "filter": {
                            "term": {
                                "paragraph_id": paragraph_id
                            }
                        },
                        "must": {
                            "match_phrase": {
                                "attachment.content": keyword_word
                            },
                        }
                    }
                }

                index_name = "doticfull_documentparagraphs_graph"
                response = client.search(index=index_name,
                                         _source_includes=['paragraph_id'],
                                         request_timeout=40,
                                         query=content_query,
                                         highlight={
                                             "order": "score",
                                             "fields": {
                                                 "attachment.content":
                                                     {
                                                         "pre_tags": ["<em>"], "post_tags": ["</em>"],
                                                         "number_of_fragments": 0
                                                     }
                                             }},
                                         size=1
                                         )

                result = response['hits']['hits']
                for row in result:
                    paragraph_id = row['_source']['paragraph_id']
                    keyword_count = row["highlight"]["attachment.content"][0].count("<em>")

                    if paragraph_id not in paragraphs_score:
                        paragraphs_score[paragraph_id] = {subject_id: keyword_count * keyword_score}
                    else:
                        if subject_id not in paragraphs_score[paragraph_id]:
                            paragraphs_score[paragraph_id][subject_id] = keyword_count * keyword_score
                        else:
                            paragraphs_score[paragraph_id][subject_id] += keyword_count * keyword_score
    Result_Create_List[thread_number] = []
    for paragraph, subject_score in paragraphs_score.items():
        normalized_subject_score = NormalizeDocumentScore(subject_score)
        topitems = heapq.nlargest(3, normalized_subject_score.items(), key=itemgetter(1))
        res = []
        for subject_id, score in dict(topitems).items():
            res.append([subject_id, score])

        subject1 = SubjectList.objects.get(id=res[0][0])
        subject1_score = res[0][1]
        subject1_name = subject1.name

        subject2 = None if res.__len__() <= 1 else SubjectList.objects.get(id=res[1][0])
        subject2_score = None if res.__len__() <= 1 else res[1][1]
        subject2_name = None if res.__len__() <= 1 else subject2.name

        subject3 = None if res.__len__() <= 2 else SubjectList.objects.get(id=res[2][0])
        subject3_score = None if res.__len__() <= 2 else res[2][1]
        subject3_name = None if res.__len__() <= 2 else subject1.name

        object = ParagraphsSubject(country=Country,
                                         paragraph_id=paragraph,
                                         version=Version,

                                         subject1=subject1,
                                         subject1_score=subject1_score,
                                         subject1_name=subject1_name,

                                         subject2=subject2,
                                         subject2_score=subject2_score,
                                         subject2_name=subject2_name,

                                         subject3=subject3,
                                         subject3_score=subject3_score,
                                         subject3_name=subject3_name
                                         )

        Result_Create_List[thread_number].append(object)


def GetSubjectSubjectGraphData(country_id, version_id):

    SubjectSubjectGraphCube.objects.filter(country_id=country_id, version_id=version_id).delete()

    Nodes_List = []
    Subject_Node_List = SubjectList.objects.filter(version_id=version_id)
    for Subject in Subject_Node_List:
        node = {"id": str(Subject.id),
                "name": Subject.name,
                "type": "rect", "size": 30,
                "style": {"fill": "#5C5CD5"}}
        Nodes_List.append(node)

    Edge_Dict = {}
    paragraph_List = ParagraphsSubject.objects.filter(country_id=country_id, version_id=version_id, document__type_id=2)

    for paragraph in paragraph_List:

        subject1 = paragraph.subject1
        subject2 = paragraph.subject2
        subject3 = paragraph.subject3

        if subject2 != None:
            edge = "_".join(sorted([str(subject1.id), str(subject2.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

        if subject3 != None:
            edge = "_".join(sorted([str(subject1.id), str(subject3.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

            edge = "_".join(sorted([str(subject2.id), str(subject3.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

        if subject2 == None and subject3 == None:
            edge = "_".join(sorted([str(subject1.id), str(subject1.id)]))
            if edge not in Edge_Dict:
                Edge_Dict[edge] = 1
            else:
                Edge_Dict[edge] += 1

    Edge_List = []
    for key, count in Edge_Dict.items():
        src_id = str(key.split("_")[0])
        src_name = SubjectList.objects.get(version_id=version_id, id=src_id).name
        target_id = str(key.split("_")[1])
        target_name = SubjectList.objects.get(version_id=version_id, id=target_id).name

        edge_obj = {"source": src_id, "source_name": src_name,
                    "target": target_id, "target_name": target_name, "weight": count}

        if src_id == target_id:
            edge_obj["type"] = "loop"

        Edge_List.append(edge_obj)

    SubjectSubjectGraphCube.objects.create(country_id=country_id, version_id=version_id, nodes_data=Nodes_List, edges_data=Edge_List)